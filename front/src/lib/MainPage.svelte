<script>
    let file;
    let responseData = null;
    let error = null;
  
    function handleFileUpload(event) {
      file = event.target.files[0];
    }
  
    async function organize() {
      if (!file) {
        alert("Please upload a ZIP file first.");
        return;
      }
  
      const formData = new FormData();
      formData.append('file', file);
  
      try {
        const res = await fetch('https://pythonanywhere/api/zipfiles', {
          method: 'POST',
          body: formData,
        });
  
        if (!res.ok) {
          throw new Error('Network response was not ok');
        }
  
        responseData = await res.json();
        console.log("Response from server:", responseData);
      } catch (err) {
        error = err.message;
        console.error("Error:", error);
      }
    }
    import '@fontsource/alfa-slab-one';
  </script>
  
  <style>
    /* CSS styles as defined earlier */
    body {
      background-color: #58F1C4; 
    } 

    .container {
      text-align: center;
      background-color: #58F1C4;
      padding: 0.1rem;
      color: white;
      width: 50%; /* Set the width to your desired value */
      margin: 0 auto; /* Center the container */
    }
  
    h1 {
      margin-bottom: 1rem;
      font-size: 2.5rem;
      font-family: 'Alfa Slab One', system-ui;
      text-shadow: 0 4px 4px rgba(0, 0, 0, 0.25);
      color: #005C4B;

    }
  
    p {
      margin-bottom: 2rem;
    }
  
    input[type="file"] {
      margin-bottom: 1rem;
      padding: 1rem;
    }
  
    button {
      padding: 1rem 2rem;
      background-color: #ffffff;
      color: #25B2A7;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
  
    button:hover {
      opacity: 0.8;
    }
  
    .links {
      margin-top: 2rem;
    }
  
    .error {
      color: red;
    }
  
    .response {
      margin-top: 20px;
      color: white;
    }
  </style>
  
  <div class="container">
    <h1>WhatsOrganizer</h1>
    <p>Organize suas conversas de WhatsApp e transcreva áudios de forma rápida e segura de uma única vez</p>
    <input type="file" accept=".zip" on:change={handleFileUpload} />
    <button on:click={organize}>Organizar!</button>
    
    {#if error}
      <p class="error">{error}</p>
    {/if}
  
    {#if responseData}
      <div class="response">
        <h2>Response Data:</h2>
        <pre>{JSON.stringify(responseData, null, 2)}</pre>
      </div>
    {/if}
  
    <div class="links">
      <a href="#">📱 Apple</a>
      <a href="#">🗂️ Limitações</a>
      <a href="#">🔒 LGPD</a>
    </div>
    
    <footer>
      <p>2024 por ProcStudio e Bruno Pellizzetti</p>
    </footer>
  </div>