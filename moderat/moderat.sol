
pragma solidity ^0.4.23;

contract Moderat{

    address owner;    //Owner of the contract, can be understood as the Steem Protocol
    mapping(bytes32 => Market) public markets; //Maps transactionID to a Post
    mapping(address => uint256) public adminsId; //Maps admins addresses to ids
    mapping(address => uint256) public rewards; //Rewards to be claimed by each user

    bytes32[] aliveMarkets;  //Markets that are either open or to be executed (w/o verdict of admins)
    bytes32[] adminsMarkets;  //Markets to be judged by the administrators of the platform
    address[] admins;  //Adminstrators of the platform
    uint numberAdmins;  //Number of admins

    uint256 constant votingTime = 120;  // (in seconds) Voting allowed window after opening of a betting market
    uint256 constant judgingTime = 120; //(in seconds) Voting window for the admins to judge on the verdict of a market
    uint256 constant judgeThreshold = 100 szabo;  //Threshold above the admins decide on the verdict of a market
    uint256 constant potThreshold = 500 szabo;  //Maximum allowed pot on a market
    uint256 constant numberMaxAdmins = 21;  //Maximum number of admins
    
    enum States {open, closed, resolved} //States in which a market can be

    struct Market{
        
        States state; //State of the market
        uint256 timeOfCreation; //When the post was created
        address[] bettors;  //Addresses of the users who have voted in the market
        bool decision;  //Verdict on the post. True = post valid | False = support flag (post unsuitable)
        uint256  total;  //Total amount bet in the market of the post
        int256 adminVoteCount;  //Voting outcome of admins. >=0 = post valid. <0 = support flag
        mapping(address => mapping(bool => uint256)) betAmounts; //maps users with outcome and amount bed
        mapping (bool => uint256) totalOutcome;  //maps the total amount bet pero outcome
        mapping(address => bool) adminVoted;  //maps which admins have voted in the post
    }

    modifier onlyAdmin{
        require (adminsId[msg.sender] != 0);
        _;
    }

    modifier onlyOwner{
        require(msg.sender == owner);
        _;
    }

    /**
    *@dev Constructor of the moderation protocol. Initial prefund over 1000 wei required.
    *@param prefundAmount Amount to be prefunded
    */
    constructor(uint256 prefundAmount) public payable {

        require(msg.value == prefundAmount);
        require(msg.value >= 1000);
        owner = msg.sender;
        addAdmin(0); //Add a dummy admin at index 0
        numberAdmins--; //Discount the dummy admin in the counter
        addAdmin(owner);  //Owner of the contract bootstraps the admins membership
    }

    //+++++++++++++++++++++++++++++++++++++++++++MARKETS+++++++++++++++++++++++++++++++++++

    /**
    *@dev Creates a new betting market associated with a post. A new market is created when a user flags a post.
    *The user is rewarded with the gas costs of executing the function and bets an extra amount on False.
    *@param postId Hash of the transaction to create the post on the blockchain.
    *@param amount Amount on the first bet on the market (False - supporting the flat)
    */
    function createTrial(bytes32 postId, uint256 amount) payable public{

    //To resemble more to Steem --> Moderation Reward Pool --> Prefunded market 

        //require --> you cannot create a trial for an already used post
        require(msg.value == amount);
        require(amount > 0);
        require(msg.value <= potThreshold);

        Market storage trial = markets[postId];
        require(trial.total == 0); //Check that the market has never been created
        trial.timeOfCreation = now;
        trial.state = States.open;
        trial.decision = false;
        trial.betAmounts[msg.sender][false] = amount;
        trial.bettors.push(msg.sender);
        trial.totalOutcome[false] = amount;
        trial.total = amount;

        aliveMarkets.push(postId);

        rewards[msg.sender] += 250; 
    }

    /**
    *@dev User bets on the voting market associated with a particular post.
    *@param postId Hash of the transaction to create the post on the blockchain
    *@param valid Supports the validity of the post (True) or the flag (False)
    *@param amount Amount to bet.
    */
    function bet(bytes32 postId, bool valid, uint256 amount) payable public{
        
        Market storage trial = markets[postId];
        
        require(now < trial.timeOfCreation + votingTime);
        require(msg.value == amount);
        require(msg.value > 0);
        require(amount <= potThreshold);
        
        //Check if the user has voted in the market, and if not, add her in the list of bettors.
        if(trial.betAmounts[msg.sender][false] == 0 && trial.betAmounts[msg.sender][true] == 0){
            trial.bettors.push(msg.sender);
        }

        trial.betAmounts[msg.sender][valid] += betWeight(now - trial.timeOfCreation,msg.value); //Include here betweight...
        trial.totalOutcome[valid] += betWeight(now - trial.timeOfCreation,msg.value);
        trial.total += msg.value;

        //The if-statement is to check if there is flip in the current winning opinion
        if (trial.decision != valid && trial.totalOutcome[valid] > trial.totalOutcome[!valid])
            trial.decision = valid;

        if(judgeThreshold <= trial.total + amount){ //judgeThreshold surpassed, admins decide!
            adminsMarkets.push(postId);
            trial.state = States.closed;
        }
        //Refund the difference to the bettor if the potThreshold is surpassed
        if(potThreshold <= trial.total + amount){

            uint256 refund = trial.total + amount - potThreshold; 
            trial.total = potThreshold;
            rewards[msg.sender] += refund;
            
        }
    }


    /**
    *@dev Execute and distribute the payout for the markets not intervened by the admins verdict.
    *It is only run by the owner of the contract (as an abstraction of the Steem protocol)
    */
    function executeMarkets() onlyOwner public{

        for(uint i = 0; i < aliveMarkets.length; i++){
            bytes32 postId = aliveMarkets[i];
            Market storage post = markets[postId];

            //Check if the voting and judging time is over and the market is not intervened
            if(now > post.timeOfCreation + votingTime + judgingTime && post.state == States.open){

                post.state = States.resolved; 
                
                remove(i,aliveMarkets);
                aliveMarkets.length--; //would be better inside remove function, but storage/memory problem
                for (uint j = 0; j < post.bettors.length; j++){

                    bool winnerDecision = post.decision;
                    address bettor = post.bettors[j];
                    uint betAmount = post.betAmounts[bettor][winnerDecision];
                    uint amountRewarded = calcFractionPot(betAmount,post.total,post.totalOutcome[winnerDecision]);

                    post.betAmounts[bettor][winnerDecision] = 0; //Avoid reentrancy
                    rewards[bettor] += amountRewarded;
                }
            }
        }
    }

    //+++++++++++++++++++++++++++++++++++++++++++++ADMINS/WITNESSES++++++++++++++++++++++++++++++++++++
    /**
    *@dev Execute and distribute the payout for the markets intervened by the admins verdict.
    *It can be run by any admin of the system.
    */
    function executeMarketsAdmins() onlyAdmin public {

        for(uint i; i < adminsMarkets.length; i++){
            bytes32 marketId = adminsMarkets[i];
            Market storage post = markets[marketId];
            //Maybe add here a minimum Quorum on the Trial
            if(now > post.timeOfCreation + votingTime + judgingTime){ 

                post.state = States.resolved;
                
                remove(i,adminsMarkets);
                adminsMarkets.length--; //would be better inside remove function, but storage/memory problem
                for (uint j; j < post.bettors.length; j++){

                    if(post.adminVoteCount > 0){winnerDecision = true;}
                    else{winnerDecision = false;}
                    bool winnerDecision = post.decision;
                    address bettor = post.bettors[j];
                    uint betAmount = post.betAmounts[bettor][winnerDecision];
                    uint amountRewarded = calcFractionPot(betAmount,post.total,post.totalOutcome[winnerDecision]);

                    post.betAmounts[bettor][winnerDecision] = 0; //Avoid reentrancy
                    rewards[bettor] += amountRewarded;
                }
            }
        }           
    }

    /**
    *@dev Select a random post from the list of alive markets.
    *@return True if selected a valid market. False if not selected a valid market.
    */
    function selectRandomPost() onlyOwner public returns(bool){ 

        require(msg.sender == owner);

        uint256 numberMarkets = aliveMarkets.length;
        require(numberMarkets > 0);
        uint256 targetTrialIndex = calculateRandom(numberMarkets);
        bytes32 targetTrial = aliveMarkets[targetTrialIndex];

        if (markets[targetTrial].timeOfCreation + votingTime >= now){

            adminsMarkets.push(targetTrial);
            remove(targetTrialIndex,aliveMarkets);
            aliveMarkets.length--; //would be better inside remove function, but storage/memory problem
            
            Market storage post = markets[targetTrial];
            post.state = States.closed;
            
            return true;
        }

        return false;
    }

    /**
    *@dev Administrators vote on the validity of a post. Only run by admins.
    *@param postId Hash of the transaction to create the post on the blockchain.
    *@param support True if support the validity of the post. False if support the flag.
    */
    function voteAdmin(bytes32 postId, bool support) onlyAdmin public {

        Market storage trial = markets[postId];
        require(!trial.adminVoted[msg.sender]);  //Check that the admin haven't vote in this market
        require(now < trial.timeOfCreation + votingTime + judgingTime);
        require(trial.state == States.closed);

        if (support){trial.adminVoteCount++;}  //If supports post, vote True
        else{trial.adminVoteCount--;}          //If supports the flag, vote False

        trial.adminVoted[msg.sender] = true;
    }

    /**
    *@dev Add admin to the administrator list. Only run by owner.
    *@param newAdmin Admin to be added.
    */
    function addAdmin(address newAdmin) onlyOwner public {
        // the <= is because admin[0] is a dummy index
        require(admins.length <= numberMaxAdmins);
        
        uint id = adminsId[newAdmin];
        if (id == 0) {
            adminsId[newAdmin] = admins.length;
            id = admins.length++;
            numberAdmins++;
        }        
    }

    /**
    *@dev Remove admin from administrator list. Only run by owner.
    *@param targetAdmin Admin to be removed.
    */
    function removeAdmin(address targetAdmin) onlyOwner public {
        require(adminsId[targetAdmin] != 0);

        for (uint i = adminsId[targetAdmin]; i<admins.length-1; i++){
            admins[i] = admins[i+1];
        }
        delete admins[admins.length-1];
        admins.length--;
        numberAdmins--;
    }

//+++++++++++++++++++++++++++++++++++++++++++GETTERS+++++++++++++++++++++++++++++++++++

    function getMarket(bytes32 postId) public view returns (
        uint    createdAt,
        bool    decision,
        States  state,
        uint    betTrue,
        uint    betFalse,
        uint    totalTrue,
        uint    totalFalse,
        uint    total,
        bool    voted
    ) {
        Market storage post = markets[postId];
        createdAt = post.timeOfCreation;
        decision = post.decision;
        state = post.state;
        betTrue = post.betAmounts[msg.sender][true];
        betFalse = post.betAmounts[msg.sender][false];
        totalTrue = post.totalOutcome[true];
        totalFalse = post.totalOutcome[false];
        total = post.total;
        voted = post.adminVoted[msg.sender];
    }

    function isBettable(bytes32 postId) public view returns(
        bool bettable,
        bool executable,
        uint createdAt,
        uint bettingTimeLeft
    ){
        Market storage post = markets[postId];
        createdAt = post.timeOfCreation;
        require(createdAt != 0);
        bettable = now < createdAt + votingTime;
        executable = now > createdAt + votingTime + judgingTime;

        if(now < createdAt + votingTime){bettingTimeLeft = createdAt + votingTime - now;}
        else{bettingTimeLeft = 0;}
    }
    
    function marketInfo() public view returns(
        uint256 numberMarketsAlive,
        uint256 numberMarketsAdmins,
        uint256 numberOfAdmins
    ) {
        numberMarketsAlive = aliveMarkets.length;
        numberMarketsAdmins = adminsMarkets.length;
        numberOfAdmins = numberAdmins;
    }

    function balanceOf() public view returns(uint256 balance){
        return address(this).balance;
    }


//+++++++++++++++++++++++++++++++++++++++++++OTHER++++++++++++++++++++++++++++++++++++++++

    /**
    * @dev Function to claim refunds and prices. Untrusted interaction with
    * untrusted contracts. Pull over push for external calls.
    */
    function untrusted_withdrawRefund() external {
        uint256 refund = rewards[msg.sender];
        rewards[msg.sender] = 0;
        msg.sender.transfer(refund);
    }

    /**
    *@dev Calculate random integer number from 0 to n.
    *@param noTrial n
    *@return Random number.
    */
    function calculateRandom(uint256 noTrials) internal view returns(uint) { 

        uint256 blockNumber = block.number - 1;
        uint256 blockHash = uint(blockhash(blockNumber));

        //Retrieving a random number within the desired range.
        uint256 targetTrial = (blockHash % noTrials);
        return targetTrial;
    }

    /**
    *@dev Calculate the fraction of the pot that one winning user can claim.
    *@param bet amount the user bet in the outcome
    *@param pot total amount bet on the market
    *@param betWinners total amount bet in the winning side.
    *@return fraction of the pot
    */
    function calcFractionPot(uint256 betAmount, uint256 pot, uint256 betWinners) pure public returns(uint){

        uint fraction = (betAmount*pot)/betWinners; // Include SafeMath library
        return fraction;
    }

    /**
    *@dev Function to weight the value of votes to incentivize early voting and to make expensive
    *flips of the market outcome at the end of the voting time.
    *@param timeElapsed time elapsed since creation of the market of the post.
    *@param amount initial bet amount
    *@return weightedAmount
    */
    function betWeight(uint256 timeElapsed, uint256 amount) pure public returns(uint256 weightedAmount){
        
        //Use SafeMath Library
        require(timeElapsed > 0);
        require(timeElapsed < votingTime);
        weightedAmount = amount - (timeElapsed * amount / (4*votingTime));//From 100% to 75% the worth of the vote

        return weightedAmount;     
    }

    /**
    *@dev Remove element from an array without leaving gaps in the middle of it. Must reduce array lenght manually.
    *@param index index of the element to be removed.
    *@param array array which element is being removed.
    */
    function remove(uint index,bytes32[] array) pure internal {
        if (index >= array.length) return;

        for (uint i = index; i<array.length-1; i++){
            array[i] = array[i+1];
        }
        delete array[array.length-1];
    }  

    /**
    *@dev Fallback function used to fund the contract (block-producers rewards)
    */
    function () public payable{
        //do-nothing
    }
}