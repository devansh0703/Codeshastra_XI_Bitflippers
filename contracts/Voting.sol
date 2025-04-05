// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./Verifier.sol";
import "./VoterNFT.sol"; // Import NFT contract

contract Voting is Ownable {
    Verifier public verifier;
    VoterNFT public voterNFT;

    constructor(address verifierAddress, address voterNFTAddress) Ownable(msg.sender) {
        verifier = Verifier(verifierAddress);
        voterNFT = VoterNFT(voterNFTAddress);
    }

    enum VoteType { Approval, RankedChoice, Quadratic }

    struct Voter {
        bool hasVoted;
    }

    mapping(address => Voter) public voters;
    mapping(uint => mapping(address => uint)) public votes;
    uint public voteId;

    event VoteCast(address indexed voter, uint indexed voteId, VoteType voteType);
    event DisputeTriggered(uint indexed voteId, string reason);

    modifier notVoted() {
        require(!voters[msg.sender].hasVoted, "Voter has already voted");
        _;
    }

    function castApprovalVote(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[3] memory input,
        uint candidateId,
        string memory tokenURI
    ) external notVoted {
        require(verifier.verifyTx(_makeProof(a, b, c), input), "Invalid ZK Proof");
        voters[msg.sender].hasVoted = true;
        votes[candidateId][msg.sender] = 1;
        voteId++;
        emit VoteCast(msg.sender, voteId, VoteType.Approval);

        _mintCertificate(msg.sender, tokenURI);
    }

    function castRankedVote(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[3] memory input,
        uint[] calldata candidateIds,
        string memory tokenURI
    ) external notVoted {
        require(verifier.verifyTx(_makeProof(a, b, c), input), "Invalid ZK Proof");
        voters[msg.sender].hasVoted = true;
        voteId++;
        emit VoteCast(msg.sender, voteId, VoteType.RankedChoice);

        _mintCertificate(msg.sender, tokenURI);
    }

    function castQuadraticVote(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c,
        uint[3] memory input,
        uint candidateId,
        uint voteTokens,
        string memory tokenURI
    ) external notVoted {
        require(verifier.verifyTx(_makeProof(a, b, c), input), "Invalid ZK Proof");
        voters[msg.sender].hasVoted = true;
        votes[candidateId][msg.sender] = voteTokens;
        voteId++;
        emit VoteCast(msg.sender, voteId, VoteType.Quadratic);

        _mintCertificate(msg.sender, tokenURI);
    }

    function triggerDispute(uint _voteId, string calldata reason) external onlyOwner {
        emit DisputeTriggered(_voteId, reason);
    }

    function _mintCertificate(address to, string memory uri) internal {
        voterNFT.mintCertificate(to, uri);
    }

    function _makeProof(
        uint[2] memory a,
        uint[2][2] memory b,
        uint[2] memory c
    ) internal pure returns (Verifier.Proof memory proof) {
        proof.a = Pairing.G1Point(a[0], a[1]);
        proof.b = Pairing.G2Point(b[0], b[1]);
        proof.c = Pairing.G1Point(c[0], c[1]);
    }
}

