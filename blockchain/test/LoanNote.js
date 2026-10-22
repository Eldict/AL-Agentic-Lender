const { expect } = require("chai");
const { ethers } = require("hardhat");

// tests for the LoanNote contract and the Green Mortgage discount.
describe("LoanNote", function () {
  let loanNote; //the deployed contract
  let owner; //the bank, it deploys the contract
  let stranger; //any other wallet
  let borrower; //the person taking the loan
  const auditHash = ethers.keccak256(ethers.toUtf8Bytes("credit memo")); //fake fingerprint of the AI memo

  // runs before every test so each one starts with a fresh contract.
  beforeEach(async function () {
    [owner, stranger, borrower] = await ethers.getSigners();
    const LoanNote = await ethers.getContractFactory("LoanNote");
    loanNote = await LoanNote.deploy();
  });

  // the wallet that deploys the contract must become the owner.
  it("sets the deployer as the owner", async function () {
    expect(await loanNote.owner()).to.equal(owner.address);
  });

  // BER A or B (any number after the letter) must get 4.75%, which is 475 basis points.
  it("gives the 0.25% discount to BER A and B ratings", async function () {
    for (const rating of ["A1", "A2", "A3", "B1", "B2", "B3"]) {
      await loanNote.mintLoan(borrower.address, 200000, 360, rating, auditHash);
      const loan = await loanNote.getLoan(await loanNote.loanCount());
      expect(loan.apr, rating).to.equal(475);
    }
  });

  // every other rating pays the normal 5.00%, which is 500 basis points.
  it("gives no discount to BER C to G ratings", async function () {
    for (const rating of ["C1", "C3", "D1", "E2", "F", "G"]) {
      await loanNote.mintLoan(borrower.address, 200000, 360, rating, auditHash);
      const loan = await loanNote.getLoan(await loanNote.loanCount());
      expect(loan.apr, rating).to.equal(500);
    }
  });

  // an empty rating must not crash and must not get the discount.
  it("gives no discount when the rating is empty", async function () {
    await loanNote.mintLoan(borrower.address, 200000, 360, "", auditHash);
    const loan = await loanNote.getLoan(1);
    expect(loan.apr).to.equal(500);
  });

  // the loan note must keep everything that was sent in, including the audit hash.
  it("stores the loan details and the audit hash", async function () {
    await loanNote.mintLoan(borrower.address, 250000, 360, "B2", auditHash);
    const loan = await loanNote.getLoan(1);
    expect(loan.borrower).to.equal(borrower.address);
    expect(loan.loanAmount).to.equal(250000);
    expect(loan.termMonths).to.equal(360);
    expect(loan.berRating).to.equal("B2");
    expect(loan.auditHash).to.equal(auditHash);
    expect(loan.isMinted).to.equal(true);
  });

  // loan ids start at 1 and go up by one for each new loan.
  it("numbers the loans 1, 2, 3", async function () {
    await loanNote.mintLoan(borrower.address, 100000, 360, "A1", auditHash);
    await loanNote.mintLoan(borrower.address, 150000, 360, "D1", auditHash);
    expect(await loanNote.loanCount()).to.equal(2);
    expect((await loanNote.getLoan(2)).loanAmount).to.equal(150000);
  });

  // minting must announce itself with the LoanMinted event.
  it("emits the LoanMinted event", async function () {
    await expect(loanNote.mintLoan(borrower.address, 200000, 360, "A1", auditHash))
      .to.emit(loanNote, "LoanMinted")
      .withArgs(1, borrower.address, 200000, 475, auditHash);
  });

  // only the owner may mint, any other wallet must be rejected.
  it("blocks anyone except the owner from minting", async function () {
    await expect(
      loanNote.connect(stranger).mintLoan(borrower.address, 200000, 360, "A1", auditHash)
    ).to.be.revertedWith("Only the owner can mint loans");
  });

  // a loan with no term makes no sense, so it must be rejected.
  it("rejects a loan with a term of zero", async function () {
    await expect(
      loanNote.mintLoan(borrower.address, 200000, 0, "A1", auditHash)
    ).to.be.revertedWith("Term must be at least 1 month");
  });
});
