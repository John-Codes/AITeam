Cypress.on("uncaught:exception", (err, runnable) => {
    // Registra el error en la consola sin que Cypress lo marque como una falla
    console.error("Uncaught exception:", err);
    return false;
  });
  