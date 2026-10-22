const hre = require("hardhat");

// the address printed by deploy.js
const CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3";

// printLoan reads a saved loan back from the blockchain and prints it.
async function printLoan(loanNote, id) {
  const loan = await loanNote.getLoan(id);
  console.log("Loan #" + id);
  console.log("  borrower:", loan.borrower);
  console.log("  amount:", loan.loanAmount.toString());
  console.log("  term (months):", loan.termMonths.toString());
  console.log("  BER rating:", loan.berRating);
  console.log("  rate:", Number(loan.apr) / 100 + "%"); //475 becomes 4.75
  console.log("  audit hash:", loan.auditHash);
}

// main plays the portal: it mints two loans and reads them back.
async function main() {
  const [bank, borrower] = await hre.ethers.getSigners(); //account 0 is the bank, account 1 is the customer
  const loanNote = await hre.ethers.getContractAt("LoanNote", CONTRACT_ADDRESS, bank);

  // the fingerprint of a made-up credit memo
  const memoHash = hre.ethers.sha256(hre.ethers.toUtf8Bytes("credit memo for loan 1"));

  await (await loanNote.mintLoan(borrower.address, 200000, 360, "B2", memoHash)).wait();//green house
  await (await loanNote.mintLoan(borrower.address, 350000, 240, "D1", memoHash)).wait(); //normal house

  await printLoan(loanNote, 1);
  await printLoan(loanNote, 2);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});