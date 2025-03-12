const elDrop = document.getElementById('drop-zone');
const elItems = document.getElementById('items');

// Highlight the drop zone on dragover
elDrop.addEventListener("dragover", (event) => {
  event.preventDefault();
  elDrop.classList.add("dragover");
});

// Remove highlight when dragging leaves the drop zone
elDrop.addEventListener("dragleave", () => {
  elDrop.classList.remove("dragover");
});

// Handle dropped files
elDrop.addEventListener('drop', async function (event) {
  event.preventDefault();
  elDrop.classList.remove("dragover");
  const items = await getAllFileEntries(event.dataTransfer.items);
  // Send the files to the server using AJAX in chunks
  try {
    for (let i = 0; i < items.length; i++) {
      await sendFilesToServer(items[i]);
    }
    console.log('All files uploaded successfully');
  } catch (error) {
    console.error('Error uploading files:', error);
  }
});

// Function to recursively get all File objects from DataTransfer items
async function getAllFileEntries(dataTransferItems) {
  let fileEntries = [];
  for (let i = 0; i < dataTransferItems.length; i++) {
    const item = dataTransferItems[i];
    const item_type = dataTransferItems[i].webkitGetAsEntry();
    if (item_type.isFile) {
      const file = item.getAsFile();
      if (file) {
        fileEntries.push(file);
      }
    } else if (item_type.isDirectory) {
      const directoryEntry = item.webkitGetAsEntry();
      if (directoryEntry.isDirectory) {
        fileEntries.push(...await getAllDirectoryEntries(directoryEntry));
      }
    }
  }
  return fileEntries;
}

async function getAllDirectoryEntries(directoryEntry) {
  let entries = [];
  return new Promise((resolve, reject) => {
    const reader = directoryEntry.createReader();
    reader.readEntries(async (results) => {
      for (let entry of results) {
        if (entry.isFile) {
          const file = await getFileFromEntry(entry);
          entries.push(file);
        } else if (entry.isDirectory) {
          entries.push(...await getAllDirectoryEntries(entry));
        }
      }
      resolve(entries);
    }, reject);
  });
}

// Function to get File object from a FileSystemFileEntry
function getFileFromEntry(fileEntry) {
  return new Promise((resolve, reject) => {
    fileEntry.file(resolve, reject);
  });
}

// Function to send files to the server using AJAX in chunks
async function sendFilesToServer(file) {
  const chunkSize = 1024 * 1024; // 1MB chunk size
  const fileSize = file.size;
  let offset = 0;

  while (offset < fileSize) {
    const blob = file.slice(offset, offset + chunkSize);
    try {
      await sendChunk(blob, file.name, offset, fileSize);
      offset += chunkSize;
    } catch (error) {
      console.error('Error uploading chunk:', error);
      throw error; // Re-throw the error to stop further uploads
    }
  }
}

// Function to send a single chunk of data
function sendChunk(chunkData, fileName, offset, fileSize) {
  return new Promise((resolve, reject) => {
    const formData = new FormData();
    formData.append('chunkData', chunkData);
    formData.append('fileName', fileName);
    formData.append('offset', offset);
    formData.append('fileSize', fileSize);

    fetch('/upload-chunk', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.message === "Chunk uploaded successfully" || data.message === "File upload complete") {
        resolve();
      } else {
        reject(new Error(`Failed to upload chunk: ${data.message}`));
      }
    })
    .catch(error => reject(error));
  });
}