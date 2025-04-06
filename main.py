# main.py
import os
import json
import uuid
import base64
import io
from datetime import datetime
from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from gradio_client import Client as GradioClient, handle_file
from web3 import Web3
from supabase import create_client, Client as SupabaseClient

# ---------------------------
# CONFIGURATION (HARD-CODED)
# ---------------------------
ALCHEMY_SEPOLIA_URL ="https://eth-sepolia.g.alchemy.com/v2/Uc1CwrZPhbHwT3kr7w3EMbBPeRaRhKC1"
PRIVATE_KEY = "d892916cb2c3a0b4dd8420b5f75bf1edcfbb84d37361921d0d646bd4c31e7bc2"
ACCOUNT_ADDRESS = "0x00281c8fCB4BA2f327dA224A21B9A2F5AE9D71B0"

VERIFIER_ADDRESS = "0x979D00cBc9a3f4bF2460596426448d2de94566B7"
VOTERNFT_ADDRESS = "0x9cF74138117A8425344B5BBC165A52c551a4d4bf"
VOTING_ADDRESS   = "0x6eea0B8A2369AebdC10978CfC6041fb5EB68F375"

SUPABASE_URL = "https://tujsdllkcxfwxjscfhss.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1anNkbGxrY3hmd3hqc2NmaHNzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4NzY5ODEsImV4cCI6MjA1OTQ1Mjk4MX0.5n9dhpTjYUxTcktfdWtIC1_dLTfoAcQbLfQjP4dfeFE"

# ---------------------------
# BLOCKCHAIN SETUP
# ---------------------------
web3 = Web3(Web3.HTTPProvider(ALCHEMY_SEPOLIA_URL))
if not web3.is_connected():
    raise Exception("Failed to connect to Sepolia via Alchemy")
account = web3.eth.account.from_key(PRIVATE_KEY)

# ---------------------------
# CONTRACT ABIs (Replace with actual ABIs)
# ---------------------------
# Minimal ABI for Voting contract (with three vote functions)
with open("Voting.json") as f:
    VOTING_ABI = json.load(f)["abi"]

with open("VoterNFT.json") as f:
    VOTERNFT_ABI = json.load(f)["abi"]

with open("Verifier.json") as f:
    VERIFIER_ABI = json.load(f)["abi"]


voting_contract = web3.eth.contract(address=VOTING_ADDRESS, abi=VOTING_ABI)
voternft_contract = web3.eth.contract(address=VOTERNFT_ADDRESS, abi=VOTERNFT_ABI)

# ---------------------------
# SUPABASE CLIENT SETUP
# ---------------------------
supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ---------------------------
# FACE VERIFICATION FUNCTIONS (Using Hugging Face Gradio API)
# ---------------------------
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

def base64_to_image(base64_str):
    if "data:" in base64_str and "base64," in base64_str:
        base64_str = base64_str.split("base64,")[1]
    img_bytes = base64.b64decode(base64_str)
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    return img

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
# DATA MODELS
# ---------------------------
class SubmitForm(BaseModel):
    full_name: str
    aadhaar_number: str
    image_base64: str

class VerifyFaceRequest(BaseModel):
    full_name: str
    aadhaar_number: str
    image_base64: str

class VoteRequest(BaseModel):
    voter_identity: str  # Aadhaar number (also used as user identity)
    candidate_id: int    # Candidate ID (assumed to be integer on-chain)
    election_id: str
    vote_type: str       # "approval", "ranked", or "quadratic"
    a: list            # List of 2 integers
    b: list            # List of two lists (each of length 2)
    c: list            # List of 2 integers
    input: list        # List of 3 integers
    tokenURI: str      # IPFS URI for NFT metadata
    voter_geolocation: str  # Voter's geolocation string

class DisputeRequest(BaseModel):
    vote_id: str
    reason: str

# ---------------------------
# ENDPOINTS
# ---------------------------

# User submission: store user data in Supabase
@app.post("/submit-form")
def submit_form(form: SubmitForm):
    if len(form.aadhaar_number) != 12 or not form.aadhaar_number.isdigit():
        raise HTTPException(status_code=400, detail="Invalid Aadhaar number")
    data = {
        "full_name": form.full_name,
        "aadhaar_number": form.aadhaar_number,
        "image_base64": form.image_base64,
        "created_at": datetime.utcnow().isoformat()
    }
    response = supabase.table("user_profiles").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to insert user data")
    return {"message": "User data submitted successfully", "data": response.data}

# Face verification: compare submitted face with stored face from Supabase
@app.post("/verify-face")
def verify_face(req: VerifyFaceRequest):
    if len(req.aadhaar_number) != 12 or not req.aadhaar_number.isdigit():
        raise HTTPException(status_code=400, detail="Invalid Aadhaar number")
    try:
        submitted_img = base64_to_image(req.image_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid submitted image data")
    response = supabase.table("user_profiles").select("image_base64").eq("aadhaar_number", req.aadhaar_number).execute()
    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=404, detail="User not found")
    stored_base64 = response.data[0]["image_base64"]
    try:
        stored_img = base64_to_image(stored_base64)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Stored image conversion failed")
    temp_submitted = "temp_submitted.png"
    temp_stored = "temp_stored.png"
    submitted_img.save(temp_submitted)
    stored_img.save(temp_stored)
    match, score = compare_face_images(temp_submitted, temp_stored)
    os.remove(temp_submitted)
    os.remove(temp_stored)
    return {"match": match, "similarity_score": score}

# Vote casting: cast a vote and mint NFT certificate based on vote type
@app.post("/vote")
def cast_vote(vote_req: VoteRequest):
    # Verify that user exists in Supabase
    user_resp = supabase.table("user_profiles").select("*").eq("aadhaar_number", vote_req.voter_identity).execute()
    if not user_resp.data or len(user_resp.data) == 0:
        raise HTTPException(status_code=404, detail="Voter not found")
    
    # Build transaction based on vote type
    nonce = web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    try:
        if vote_req.vote_type.lower() == "approval":
            tx = voting_contract.functions.castApprovalVote(
                vote_req.a,
                vote_req.b,
                vote_req.c,
                vote_req.input,
                vote_req.candidate_id,
                vote_req.tokenURI
            ).buildTransaction({
                "from": ACCOUNT_ADDRESS,
                "nonce": nonce,
                "gas": 600000,
                "gasPrice": web3.toWei("10", "gwei")
            })
        elif vote_req.vote_type.lower() == "ranked":
            tx = voting_contract.functions.castRankedVote(
                vote_req.a,
                vote_req.b,
                vote_req.c,
                vote_req.input,
                [vote_req.candidate_id],  # For simplicity, assume one candidate for ranked vote
                vote_req.tokenURI
            ).buildTransaction({
                "from": ACCOUNT_ADDRESS,
                "nonce": nonce,
                "gas": 700000,
                "gasPrice": web3.toWei("10", "gwei")
            })
        elif vote_req.vote_type.lower() == "quadratic":
            # For quadratic voting, assume voteTokens is provided in the input[2] (or add a new field if needed)
            voteTokens = vote_req.input[2]
            tx = voting_contract.functions.castQuadraticVote(
                vote_req.a,
                vote_req.b,
                vote_req.c,
                vote_req.input,
                vote_req.candidate_id,
                voteTokens,
                vote_req.tokenURI
            ).buildTransaction({
                "from": ACCOUNT_ADDRESS,
                "nonce": nonce,
                "gas": 800000,
                "gasPrice": web3.toWei("10", "gwei")
            })
        else:
            raise HTTPException(status_code=400, detail="Invalid vote type")
        
        signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blockchain transaction failed: {str(e)}")
    
    # Record vote in Supabase
    vote_id = str(uuid.uuid4())
    vote_data = {
        "vote_id": vote_id,
        "voter_identity": vote_req.voter_identity,
        "candidate_id": str(vote_req.candidate_id),
        "election_id": vote_req.election_id,
        "voter_geolocation": vote_req.voter_geolocation,
        "blockchain_tx_hash": tx_receipt.transactionHash.hex(),
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("votes").insert(vote_data).execute()
    
    # Mint NFT certificate by calling VoterNFT contract
    try:
        nonce = web3.eth.get_transaction_count(ACCOUNT_ADDRESS)
        tx_nft = voternft_contract.functions.mintCertificate(
            vote_req.voter_identity,
            vote_req.tokenURI
        ).buildTransaction({
            "from": ACCOUNT_ADDRESS,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": web3.toWei("10", "gwei")
        })
        signed_tx_nft = web3.eth.account.sign_transaction(tx_nft, PRIVATE_KEY)
        nft_tx_hash = web3.eth.send_raw_transaction(signed_tx_nft.rawTransaction)
        nft_receipt = web3.eth.wait_for_transaction_receipt(nft_tx_hash)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NFT minting failed: {str(e)}")
    
    # Record certificate details in Supabase
    certificate_id = str(uuid.uuid4())
    certificate_data = {
        "certificate_id": certificate_id,
        "voter_identity": vote_req.voter_identity,
        "election_id": vote_req.election_id,
        "nft_token_id": "TBD",  # Parse token ID from nft_receipt events if needed
        "blockchain_tx_hash": nft_receipt.transactionHash.hex(),
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("nft_certificates").insert(certificate_data).execute()
    
    # Store ZKP proof details in Supabase
    zkp_id = str(uuid.uuid4())
    zkp_data = {
        "verification_id": zkp_id,
        "vote_id": vote_id,
        "zkp_proof": json.dumps({
            "a": vote_req.a,
            "b": vote_req.b,
            "c": vote_req.c,
            "input": vote_req.input
        }),
        "created_at": datetime.utcnow().isoformat()
    }
    supabase.table("zkp_verifications").insert(zkp_data).execute()
    
    return {
        "message": "Vote cast successfully and NFT certificate minted",
        "vote_tx": tx_receipt.transactionHash.hex(),
        "nft_tx": nft_receipt.transactionHash.hex()
    }

# Dispute endpoint: Initiate a dispute on a vote
@app.post("/dispute")
def initiate_dispute(dispute: DisputeRequest):
    dispute_id = str(uuid.uuid4())
    dispute_data = {
        "id": dispute_id,
        "vote_id": dispute.vote_id,
        "reason": dispute.reason,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat()
    }
    # Store dispute in Supabase (assume table 'disputes' exists)
    supabase.table("disputes").insert(dispute_data).execute()
    return {"message": "Dispute initiated", "dispute": dispute_data}

# Results endpoint: Retrieve aggregated election results
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

# ---------------------------
# Run the FastAPI Application
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

