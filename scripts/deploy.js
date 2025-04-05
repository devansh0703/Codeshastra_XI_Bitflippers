async function main() {
    const [deployer] = await ethers.getSigners();

    const Verifier = await ethers.getContractFactory("Verifier");
    const verifier = await Verifier.deploy();
    await verifier.deployed();

    const VoterNFT = await ethers.getContractFactory("VoterNFT");
    const nft = await VoterNFT.deploy();
    await nft.deployed();

    const Voting = await ethers.getContractFactory("Voting");
    const voting = await Voting.deploy(verifier.address, nft.address);
    await voting.deployed();

    // Make Voting contract the owner of NFT contract
    await nft.transferOwnership(voting.address);

    console.log("Verifier deployed to:", verifier.address);
    console.log("VoterNFT deployed to:", nft.address);
    console.log("Voting deployed to:", voting.address);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});

