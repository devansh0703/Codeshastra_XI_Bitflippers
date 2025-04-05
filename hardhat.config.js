require("@nomiclabs/hardhat-ethers");

module.exports = {
  solidity: "0.8.28",
  networks: {
    sepolia: {
      url: `https://eth-sepolia.g.alchemy.com/v2/Uc1CwrZPhbHwT3kr7w3EMbBPeRaRhKC1`,
      accounts: [`d892916cb2c3a0b4dd8420b5f75bf1edcfbb84d37361921d0d646bd4c31e7bc2`],
    },
  },
};

