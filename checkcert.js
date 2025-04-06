(async () => {
  const [signer] = await ethers.getSigners();
  const VoterNFT = await ethers.getContractFactory("VoterNFT");
  const nft = VoterNFT.attach("0x9cF74138117A8425344B5BBC165A52c551a4d4bf");

  const balance = await nft.balanceOf(signer.address);
  console.log("NFTs owned by", signer.address, ":", balance.toString());
})();
