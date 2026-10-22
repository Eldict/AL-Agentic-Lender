const hre = require("hardhat");

// main deploys the LoanNote contract and prints where it ended up.
async function main() {
  const LoanNote = await hre.ethers.getContractFactory("LoanNote");
  const loanNote = await LoanNote.deploy(); //the wallet running this script becomes the owner
  await loanNote.waitForDeployment(); //waits until the contract is really on the chain

  console.log("LoanNote deployed to:", await loanNote.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
