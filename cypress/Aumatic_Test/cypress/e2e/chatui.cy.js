describe("ChatUI Page Tests", () => {
  beforeEach(() => {
    // Before each test, visit the chatui page
    cy.visit("http://127.0.0.1:8000/aiteam/");
  });

  it("Should send a message when Enter key is pressed", () => {
    const message = "Hello, show me how to config a cypress for a proyect";

    // Type a message in the input and press Enter
    cy.get("#userMessage").type(`${message}{enter}`);

    // Verify that the message is sent correctly
    cy.get(".message-right .message-content").last().should("contain", message);
  });

  it("Should send a message when the 'Send' button is clicked", () => {
    const message = "Hello, for what's the it function en cypress";

    // Type a message in the input
    cy.get("#userMessage").type(message);

    // Click the 'Send' button
    cy.get(".btn-send").click();

    // Verify that the message is sent correctly
    cy.get(".message-right .message-content").last().should("contain", message);
  });

  it("Should clear the input after sending a message", () => {
    const message = "how i install cypress for test my site-web make on django framework";

    // Type a message in the input and press Enter
    cy.get("#userMessage").type(`${message}{enter}`);

    // Verify that the input is empty after sending the message
    cy.get("#userMessage").should("have.value", "");
  });
  it("Should show the menu when checkbox is checked", () => {
    // Verifica que el menú no esté visible inicialmente
    cy.get(".menu-items").should("not.be.visible");

    // Haz clic en el label asociado al checkbox para activarlo
    cy.get("label[for='hamburgerToggle']").click();

    // Verifica que el menú esté visible después de hacer clic en el checkbox
    cy.get(".menu-items").should("be.visible");
  });

  it("Should hide the menu when checkbox is unchecked", () => {
    // Haz clic en el label asociado al checkbox para desactivarlo
    cy.get("label[for='hamburgerToggle']").click();

    // Verifica que el menú esté visible antes de hacer clic en el checkbox
    cy.get(".menu-items").should("be.visible");

    // Haz clic nuevamente en el label asociado al checkbox para desactivarlo
    cy.get("label[for='hamburgerToggle']").click();

    // Verifica que el menú esté oculto después de hacer clic nuevamente en el checkbox
    cy.get(".menu-items").should("not.be.visible");
  });

});
