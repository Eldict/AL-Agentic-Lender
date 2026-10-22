// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

// LoanNote is the on-chain record of every approved mortgage.
// Once a loan is minted here it can be read by anyone but never changed.
contract LoanNote {
    // Loan is one minted loan note.
    struct Loan {
        address borrower;
        uint256 loanAmount;
        uint256 apr; // in basis points. 500 = 5.00%, 475 = 4.75%
        string berRating;
        bytes32 auditHash; // fingerprint of the AI credit memo, proves it was not edited later
        uint256 timestamp;
        bool isMinted;
    }

    // owner is the wallet that deployed the contract (the bank). only it can mint loans.
    address public owner;

    mapping(uint256 => Loan) public loans;
    uint256 public loanCount;

    event LoanMinted(uint256 loanId, address borrower, uint256 amount, uint256 apr, bytes32 auditHash);

    // the wallet that deploys the contract becomes the owner.
    constructor() {
        owner = msg.sender;
    }

    // onlyOwner stops any other wallet from calling the function it is attached to.
    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can mint loans");
        _; //runs the rest of the function
    }

    // mintLoan works out the APR, saves the loan note and announces it with an event.
    function mintLoan(
        address _borrower,
        uint256 _loanAmount,
        string memory _berRating,
        bytes32 _auditHash
    ) public onlyOwner returns (uint256) {
        uint256 apr = calculateAPR(_berRating); //green discount is applied here

        loanCount++; //loan ids start at 1
        loans[loanCount] = Loan({
            borrower: _borrower,
            loanAmount: _loanAmount,
            apr: apr,
            berRating: _berRating,
            auditHash: _auditHash,
            timestamp: block.timestamp,
            isMinted: true
        });

        emit LoanMinted(loanCount, _borrower, _loanAmount, apr, _auditHash);
        return loanCount;
    }

    // calculateAPR is the Green Mortgage incentive: BER A or B gets 0.25% off.
    // irish ratings look like A1, A2, B3 so only the first letter is checked.
    function calculateAPR(string memory _berRating) internal pure returns (uint256) {
        bytes memory rating = bytes(_berRating);
        if (rating.length == 0) {
            return 500; //no rating = no discount
        }

        bytes1 band = rating[0]; //the letter part of the rating
        if (band == "A" || band == "B") {
            return 475;
        }
        return 500;
    }

    // getLoan lets anyone look up a loan note by its id.
    function getLoan(uint256 _loanId) public view returns (Loan memory) {
        return loans[_loanId];
    }
}
