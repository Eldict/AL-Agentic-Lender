// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoanNote {
    struct Loan {
        address borrower;
        uint256 loanAmount;
        uint256 apr;
        string berRating;
        uint256 timestamp;
        bool isMinted;
    }

    mapping(uint256 => Loan) public loans;
    uint256 public loanCount;

    event LoanMinted(uint256 loanId, address borrower, uint256 amount, uint256 apr);

    function mintLoan(
        address _borrower,
        uint256 _loanAmount,
        string memory _berRating
    ) public returns (uint256) {
        uint256 apr = calculateAPR(_berRating);
        
        loanCount++;
        loans[loanCount] = Loan({
            borrower: _borrower,
            loanAmount: _loanAmount,
            apr: apr,
            berRating: _berRating,
            timestamp: block.timestamp,
            isMinted: true
        });

        emit LoanMinted(loanCount, _borrower, _loanAmount, apr);
        return loanCount;
    }

    function calculateAPR(string memory _berRating) internal pure returns (uint256) {
        if (keccak256(bytes(_berRating)) == keccak256(bytes("A")) ||
            keccak256(bytes(_berRating)) == keccak256(bytes("B"))) {
            return 475;
        }
        return 500;
    }

    function getLoan(uint256 _loanId) public view returns (Loan memory) {
        return loans[_loanId];
    }
}