// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract VoterNFT is ERC721URIStorage, Ownable {
    uint public tokenCounter;

    // Pass the deployer as the owner to the Ownable constructor
    constructor() ERC721("VoterCertificate", "VOTE") Ownable(msg.sender) {
        tokenCounter = 0;
    }
    
    // Mint an NFT certificate to a voter address
    function mintCertificate(address recipient, string memory tokenURI) external onlyOwner returns (uint) {
        uint tokenId = tokenCounter;
        _safeMint(recipient, tokenId);
        _setTokenURI(tokenId, tokenURI);
        tokenCounter++;
        return tokenId;
    }
}

