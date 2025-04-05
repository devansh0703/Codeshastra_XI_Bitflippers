// scripts/uploadMetadata.js

const { NFTStorage, File } = require('nft.storage');
const fs = require('fs');
const path = require('path');

const client = new NFTStorage({ token: ec4dbb68.f98ff872ebc348a98d7074663257ab31 });

async function uploadCertificate(name, description, imagePath) {
  const imageFile = new File([fs.readFileSync(imagePath)], path.basename(imagePath), { type: 'image/png' });

  const metadata = await client.store({
    name,
    description,
    image: imageFile
  });

  console.log("Metadata URI:", metadata.url);
  return metadata.url;
}

module.exports = { uploadCertificate };

