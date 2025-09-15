<script>
    import { onMount } from 'svelte';
    import { PUBLIC_API_URL } from '$env/static/public';
  
    let fileInput;
    let result = null;
    let isLoading = false;
    let error = null;
  
    async function handleSubmit() {
      if (!fileInput.files[0]) {
        error = "Please select a ZIP file first.";
        return;
      }
  
      const file = fileInput.files[0];
      if (!file.name.endsWith('.zip')) {
        error = "Please select a ZIP file.";
        return;
      }
  
      error = null;
      isLoading = true;
      result = null;
  
      const formData = new FormData();
      formData.append('file', file);
  
      try {
        const response = await fetch(`${PUBLIC_API_URL}/process`, {
          method: 'POST',
          body: formData,
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        result = await response.json();
      } catch (e) {
        console.error("There was an error processing the file:", e);
        error = "There was an error processing the file. Please try again.";
      } finally {
        isLoading = false;
      }
    }
  
    onMount(() => {
      // Any initialization code can go here
    });
  </script>
  
  <main>
    <h1>ZIP File Processor</h1>
    
    <div>
      <input type="file" bind:this={fileInput} accept=".zip" />
      <button on:click={handleSubmit} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Send'}
      </button>
    </div>
  
    {#if error}
      <p class="error">{error}</p>
    {/if}
  
    {#if result}
      <h2>Result:</h2>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    {/if}
  </main>
  
  <style>
    main {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }
  
    input[type="file"] {
      margin-right: 10px;
    }
  
    button {
      padding: 10px 20px;
      background-color: #4CAF50;
      color: white;
      border: none;
      cursor: pointer;
    }
  
    button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
    }
  
    .error {
      color: red;
    }
  
    pre {
      background-color: #f4f4f4;
      padding: 10px;
      overflow-x: auto;
    }
  </style>