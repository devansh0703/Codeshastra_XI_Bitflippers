// scripts/uploadToNFTStorage.js

const fs = require("fs");
const path = require("path");
const axios = require("axios");
const FormData = require("form-data");

const NFT_STORAGE_API_KEY = "ec4dbb68.f98ff872ebc348a98d7074663257ab31"; // Don't share this key publicly

async function uploadToNFTStorage(filePath) {
  const fullPath = path.resolve(filePath);
  const fileStream = fs.createReadStream(fullPath);

  const formData = new FormData();
  formData.append("file", fileStream);

  const response = await axios.post(
    "https://api.nft.storage/upload",
    formData,
    {
      headers: {
        Authorization: `Bearer ${NFT_STORAGE_API_KEY}`,
        ...formData.getHeaders(),
      },
    }
  );

  if (response.status === 200) {
    const cid = response.data.value.cid;
    console.log("✅ Uploaded to IPFS via NFT.Storage");
    console.log("IPFS URI:", `ipfs://${cid}`);
    return `ipfs://${cid}`;
  } else {
    throw new Error("Failed to upload file to NFT.Storage");
  }
}

// Example usage:
uploadToNFTStorage("./metadata/voterCertificate.json")
  .then((uri) => console.log("✅ URI:", uri))
  .catch((err) => console.error("❌ Error uploading:", err));

