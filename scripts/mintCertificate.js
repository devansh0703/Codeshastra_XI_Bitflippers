
const { ethers } = require("hardhat");
const { uploadCertificate } = require('./uploadMetadata');

async function main(voterAddress) {
    const [deployer] = await ethers.getSigners();

    const VoterNFT = await ethers.getContractAt("VoterNFT", "<DEPLOYED_VOTERNFT_ADDRESS>");
    
    // Step 1: Upload metadata to IPFS
    const metadataURI = await uploadCertificate(
        "Vote Certificate",
        `Certificate for voting on ${new Date().toDateString()}`,
        "./metadata/vote-badge.png"
    );

    // Step 2: Mint the NFT
    const tx = await VoterNFT.connect(deployer).mintCertificate(voterAddress, metadataURI);
    await tx.wait();
    console.log("NFT Minted for:", voterAddress);
}

main("0xYourVoterAddressHere")
    .then(() => process.exit(0))
    .catch((err) => {
        console.error(err);
        process.exit(1);
    });

