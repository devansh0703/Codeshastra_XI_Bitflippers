// uploadtoNFTStorage.js

const fs = require("fs");
const path = require("path");
const axios = require("axios");
const FormData = require("form-data");

// Your NFT.Storage API key (keep this secure in production)
const NFT_STORAGE_API_KEY = "ec4dbb68.f98ff872ebc348a98d7074663257ab31";

/**
 * Uploads the specified file to NFT.Storage.
 * @param {string} filePath - The local file path to the file to upload.
 * @returns {Promise<string>} - Resolves to the IPFS URI (e.g., "ipfs://CID").
 */
async function uploadToNFTStorage(filePath) {
  try {
    const fullPath = path.resolve(filePath);
    const fileStream = fs.createReadStream(fullPath);

    const formData = new FormData();
    formData.append("file", fileStream);

    const response = await axios.post("https://api.nft.storage/upload", formData, {
      headers: {
        Authorization: `Bearer ${NFT_STORAGE_API_KEY}`,
        ...formData.getHeaders(),
      },
    });

    if (response.status === 200 && response.data && response.data.value && response.data.value.cid) {
      const cid = response.data.value.cid;
      console.log("✅ Uploaded to NFT.Storage");
      console.log("IPFS URI:", `ipfs://${cid}`);
      // Write the CID to a file for later use
      fs.writeFileSync("cid.txt", cid, "utf8");
      return `ipfs://${cid}`;
    } else {
      throw new Error("Failed to upload file to NFT.Storage. Response: " + JSON.stringify(response.data));
    }
  } catch (error) {
    console.error("❌ Error uploading to NFT.Storage:", error.message);
    throw error;
  }
}

// Example usage:
// Upload a file (e.g., NFT metadata JSON file) and log the resulting IPFS URI.
uploadToNFTStorage("./metadata/voterCertificate.json")
  .then((uri) => console.log("✅ Final IPFS URI:", uri))
  .catch((err) => console.error(err));

module.exports = { uploadToNFTStorage };
