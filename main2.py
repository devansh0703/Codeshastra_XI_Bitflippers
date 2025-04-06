# main.py

import os
import json
import uuid
import base64
import io
import subprocess
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from gradio_client import Client as GradioClient, handle_file
from web3 import Web3
from supabase import create_client, Client as SupabaseClient

# ---------------------------
# CONFIGURATION (HARD-CODED)
# ---------------------------
ALCHEMY_SEPOLIA_URL = "https://eth-sepolia.g.alchemy.com/v2/Uc1CwrZPhbHwT3kr7w3EMbBPeRaRhKC1"
PRIVATE_KEY = "d892916cb2c3a0b4dd8420b5f75bf1edcfbb84d37361921d0d646bd4c31e7bc2"  # (Global key for non-vote ops if needed)
ACCOUNT_ADDRESS = "0x00281c8fCB4BA2f327dA224A21B9A2F5AE9D71B0"

VERIFIER_ADDRESS = "0x979D00cBc9a3f4bF2460596426448d2de94566B7"
VOTERNFT_ADDRESS = "0x9cF74138117A8425344B5BBC165A52c551a4d4bf"
VOTING_ADDRESS   = "0x6eea0B8A2369AebdC10978CfC6041fb5EB68F375"

SUPABASE_URL = "https://tujsdllkcxfwxjscfhss.supabase.co"
SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1anNkbGxrY3hmd3hqc2NmaHNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzY5ODEsImV4cCI6MjA1OTQ1Mjk4MX0."
    "5n9dhpTjYUxTcktfdWtIC1_dLTfoAcQbLfQjP4dfeFE"
)

NFT_STORAGE_API_KEY = "ec4dbb68.f98ff872ebc348a98d7074663257ab31"

# ---------------------------
# BLOCKCHAIN SETUP
# ---------------------------
web3 = Web3(Web3.HTTPProvider(ALCHEMY_SEPOLIA_URL))
if not web3.is_connected():
    raise Exception("Failed to connect to Sepolia via Alchemy")
# Note: For vote transactions, we use the voter's provided private key.
account = web3.eth.account.from_key(PRIVATE_KEY)

# ---------------------------
# CONTRACT ABIs: Load from JSON files (placed in the same directory)
# ---------------------------
with open("Voting.json") as f:
    VOTING_ABI = json.load(f)["abi"]
with open("VoterNFT.json") as f:
    VOTERNFT_ABI = json.load(f)["abi"]
with open("Verifier.json") as f:
    VERIFIER_ABI = json.load(f)["abi"]

voting_contract = web3.eth.contract(address=VOTING_ADDRESS, abi=VOTING_ABI)
voternft_contract = web3.eth.contract(address=VOTERNFT_ADDRESS, abi=VOTERNFT_ABI)
# (The Verifier contract is deployed on-chain and used by Voting.sol.)

# ---------------------------
# SUPABASE CLIENT SETUP
# ---------------------------
supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ---------------------------
# HELPER FUNCTIONS
# ---------------------------
def base64_to_image(base64_str):
    if "data:" in base64_str and "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]
    img_bytes = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(img_bytes))

def compare_face_images(img1_path, img2_path):
    try:
        hf_client = GradioClient("erfanakk/face-Verification")
        frame1 = handle_file(img1_path)
        frame2 = handle_file(img2_path)
        result = hf_client.predict(
            frame1=frame1,
            frame2=frame2,
            model_name="buffalo_s",
            api_name="/compare_face"
        )
        if isinstance(result, tuple) and len(result) > 0 and isinstance(result[0], dict):
            is_match = result[0].get("same_person", False)
            similarity_score = 1.0 if is_match else 0.0
            return is_match, similarity_score
        return False, 0.0
    except Exception as e:
        print(f"Face comparison error: {str(e)}")
        return False, 0.0

def generate_zkp():
    """
    Return the actual proof parameters as provided.
    """
    a = [
      "0x0edde5853797c7fa3803876ddc8a49c9c1426da8f60ec579f7d97c20ebe7c51a",
      "0x1b922cb539dbd3aed5be46ec8a08fa3a5eaaa00d03e19e87e0798f9fa2385179"
    ]
    b = [
      [
        "0x201de1b831026d331c47b34ab6fc136286199fb2d1055468f74b482aebdf549e",
        "0x2e33351df522e41bf723c208a73bbe0f1e9ce71cec4ef28f4064d80ca519ec65"
      ],
      [
        "0x1f822eba7c6150b38f319e1d39fd37ec60aaf6e06f19a3b08e2f5a42cf461397",
        "0x0eb3410a0e862846f5cf278fa7dfe019ab01d70f335063894256dad1a00a89e1"
      ]
    ]
    c = [
      "0x23c8b5b8b05c25c842bc5d1a0ecd3b80534089cdaefbe7c5eabc3af1cd2e1a6c",
      "0x2a63222e4eaf1361d353f3e4e762005a93060962d7b2ae42c258d4aaa3c31a5e"
    ]
    inputs = [
      "0x00000000000000000000000000000000000000000000000000000000075bcd15",
      "0x000000000000000000000000000000000000000000000000000000003ade68b1",
      "0x0000000000000000000000000000000000000000000000000000000000000000"
    ]
    return a, b, c, inputs

def upload_certificate_metadata():
    """
    Call the external Node.js script "uploadtoNFTStorage.js" to upload NFT metadata.
    The script should upload the file (e.g., "./metadata/voterCertificate.json") and write the resulting CID to "cid.txt".
    """
    try:
        subprocess.run(["node", "uploadtoNFTStorage.js"], check=True)
        with open("cid.txt", "r") as f:
            cid = f.read().strip()
        return f"ipfs://{cid}"
    except Exception as e:
        raise Exception(f"NFT metadata upload failed: {str(e)}")

# ---------------------------
# FASTAPI APP SETUP
# ---------------------------
app = FastAPI(title="Blockchain Voting Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Pydantic Models (Matching your schema)
# ---------------------------
class RegisterRequest(BaseModel):
    identity_number: str  # Aadhaar number
    full_name: str
    email: str
    password: str
    image_base64: str

class LoginRequest(BaseModel):
    identity_number: str
    password: str
    image_base64: str  # Fresh image for face verification

# Note: We change candidate_id to a string because it is a UUID in your DB.
class VoteRequest(BaseModel):
    voter_identity: str           # Aadhaar number
    candidate_id: str             # Candidate ID as UUID (will be converted)
    election_id: str
    vote_type: str                # "approval", "ranked", or "quadratic"
    voter_geolocation: str
    private_key: str              # Voter's private key for signing transactions

class DisputeRequest(BaseModel):
    vote_id: str
    reason: str

# ---------------------------
# ENDPOINTS
# ---------------------------

@app.post("/register")
def register_user(req: RegisterRequest):
    if len(req.identity_number) != 12 or not req.identity_number.isdigit():
        raise HTTPException(status_code=400, detail="Invalid Aadhaar number")
    user_data = {
        "identity_number": req.identity_number,
        "name": req.full_name,
        "email": req.email,
        "password_hash": req.password,  # Plain text for simplicity
        "role": "voter",
        "image_base64": req.image_base64,
        "created_at": datetime.utcnow().isoformat()
    }
    response = supabase.table("users").insert(user_data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Registration failed")
    return {"message": "User registered successfully", "data": response.data}

@app.post("/login")
def login_user(req: LoginRequest):
    if len(req.identity_number) != 12 or not req.identity_number.isdigit():
        raise HTTPException(status_code=400, detail="Invalid Aadhaar number")
    result = supabase.table("users").select("*").eq("identity_number", req.identity_number).execute()
    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    user = result.data[0]
    if user["password_hash"] != req.password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    try:
        stored_img = base64_to_image(user["image_base64"])
        submitted_img = base64_to_image(req.image_base64)
        temp_stored = "temp_stored.png"
        temp_submitted = "temp_submitted.png"
        stored_img.save(temp_stored)
        submitted_img.save(temp_submitted)
        match, score = compare_face_images(temp_stored, temp_submitted)
        os.remove(temp_stored)
        os.remove(temp_submitted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face verification failed: {str(e)}")
    if not match:
        raise HTTPException(status_code=401, detail="Face verification failed")
    return {"message": "Login successful", "similarity_score": score, "user": user}

@app.get("/elections")
def list_elections():
    response = supabase.table("elections").select("*").execute()
    return {"elections": response.data}

@app.post("/vote")
def cast_vote(vote_req: VoteRequest):
    # Verify voter exists
    user_resp = supabase.table("users").select("*").eq("identity_number", vote_req.voter_identity).execute()
    if not user_resp.data:
        raise HTTPException(status_code=404, detail="Voter not found")
   
    # Use provided private key to sign transactions
    try:
        voter_account = web3.eth.account.from_key(vote_req.private_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid private key")
   
    # Generate ZKP proof parameters using actual values from your ZoKrates circuit
    try:
        a, b, c, inputs = generate_zkp()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
   
    # Upload NFT certificate metadata via NFT.Storage using your actual script
    try:
        tokenURI = upload_certificate_metadata()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NFT metadata upload failed: {str(e)}")
   
    # Convert candidate_id (UUID string) to an integer for the blockchain vote.
    # For example, remove hyphens and parse as a hex integer.
    try:
        candidate_int = int(vote_req.candidate_id.replace("-", ""), 16)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid candidate_id format")
   
    nonce = web3.eth.get_transaction_count(voter_account.address)
    try:
        if vote_req.vote_type.lower() == "approval":
            tx = voting_contract.functions.castApprovalVote(
                a, b, c, inputs,
                candidate_int,
                tokenURI
            ).buildTransaction({
                "from": voter_account.address,
                "nonce": nonce,
                "gas": 600000,
                "gasPrice": web3.toWei("10", "gwei")
            })
        elif vote_req.vote_type.lower() == "ranked":
            tx = voting_contract.functions.castRankedVote(
                a, b, c, inputs,
                [candidate_int],
                tokenURI
            ).buildTransaction({
                "from": voter_account.address,
                "nonce": nonce,
                "gas": 700000,
                "gasPrice": web3.toWei("10", "gwei")
            })
        elif vote_req.vote_type.lower() == "quadratic":
            voteTokens = inputs[2]
            tx = voting_contract.functions.castQuadraticVote(
                a, b, c, inputs,
                candidate_int,
                voteTokens,
                tokenURI
            ).buildTransaction({
                "from": voter_account.address,
                "nonce": nonce,
                "gas": 800000,
                "gasPrice": web3.toWei("10", "gwei")
            })
        else:
            raise HTTPException(status_code=400, detail="Invalid vote type")
       
        signed_tx = web3.eth.account.sign_transaction(tx, vote_req.private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain vote failed: {str(e)}")
   
    vote_id = str(uuid.uuid4())
    vote_data = {
        "vote_id": vote_id,
        "voter_identity": vote_req.voter_identity,
        "candidate_id": vote_req.candidate_id,
        "election_id": vote_req.election_id,
        "voter_geolocation": vote_req.voter_geolocation,
        "blockchain_tx_hash": tx_receipt.transactionHash.hex(),
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("votes").insert(vote_data).execute()
   
    # Mint NFT Certificate using voter's account
    try:
        nonce = web3.eth.get_transaction_count(voter_account.address)
        tx_nft = voternft_contract.functions.mintCertificate(
            vote_req.voter_identity,
            tokenURI
        ).buildTransaction({
            "from": voter_account.address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": web3.toWei("10", "gwei")
        })
        signed_tx_nft = web3.eth.account.sign_transaction(tx_nft, vote_req.private_key)
        nft_tx_hash = web3.eth.send_raw_transaction(signed_tx_nft.rawTransaction)
        nft_receipt = web3.eth.wait_for_transaction_receipt(nft_tx_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NFT minting failed: {str(e)}")
   
    certificate_id = str(uuid.uuid4())
    certificate_data = {
        "certificate_id": certificate_id,
        "voter_identity": vote_req.voter_identity,
        "election_id": vote_req.election_id,
        "nft_token_id": "TBD",  # Optionally, parse token ID from nft_receipt events if available
        "blockchain_tx_hash": nft_receipt.transactionHash.hex(),
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("nft_certificates").insert(certificate_data).execute()
   
    zkp_id = str(uuid.uuid4())
    zkp_data = {
        "verification_id": zkp_id,
        "vote_id": vote_id,
        "zkp_proof": json.dumps({ "a": a, "b": b, "c": c, "input": inputs }),
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("zkp_verifications").insert(zkp_data).execute()
   
    return {
        "message": "Vote cast successfully and NFT certificate minted",
        "vote_tx": tx_receipt.transactionHash.hex(),
        "nft_tx": nft_receipt.transactionHash.hex()
    }

@app.post("/dispute")
def initiate_dispute(dispute: DisputeRequest):
    dispute_data = {
        "id": str(uuid.uuid4()),
        "vote_id": dispute.vote_id,
        "reason": dispute.reason,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("disputes").insert(dispute_data).execute()
    return {"message": "Dispute initiated", "dispute": dispute_data}

@app.get("/results")
def get_results(election_id: str):
    response = supabase.table("votes").select("*").eq("election_id", election_id).execute()
    if not response.data:
        return {"results": {}}
    results = {}
    for vote in response.data:
        candidate = vote["candidate_id"]
        results[candidate] = results.get(candidate, 0) + 1
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

