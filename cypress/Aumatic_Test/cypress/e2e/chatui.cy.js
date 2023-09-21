describe("ChatUI Page Tests", () => {
  beforeEach(() => {
    cy.visit("http://127.0.0.1:8000/ai-team/");
  });

  it("Should send a message when Enter key is pressed", () => {
    const message = "Whats AI Team";
    cy.get("#userMessage").type(`${message}{enter}`);
    cy.get(".message-right .message-content").last().should("contain", message);
    cy.wait(3000);
    cy.get(".chat-body").last();
  });

  it("Should send a message when the 'Send' button is clicked", () => {
    const message = "How AI Team can help me maintain good programming practices";
    cy.get("#userMessage").type(message);
    cy.get(".btn-send").click();
    cy.get(".message-right .message-content").last().should("contain", message);
    cy.wait(3000);
    cy.get(".message-left").last();
  });

  it("Should clear the input after sending a message", () => {
    const message = "How do I install Cypress to test my Django website";
    cy.get("#userMessage").type(`${message}{enter}`);
    cy.get("#userMessage").should("have.value", "");
  });

  it("Should show the menu when checkbox is checked", () => {
    cy.get(".menu-items").should("not.be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
  });

  it("Should hide the menu when checkbox is unchecked", () => {
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("not.be.visible");
  });

  it("Should send a message 'What is AiTeam' when Enter key is pressed", () => {
    const message = "What is AiTeam";
    cy.get("#userMessage").type(`${message}{enter}`);
    cy.get(".message-right .message-content").last().should("contain", message);
  });

  it("Should navigate to 'Home' when 'Home' is clicked in the menu", () => {
    cy.get(".menu-items").should("not.be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
    cy.contains("a", "Home").click();
    cy.url().should("eq", "http://127.0.0.1:8000/ai-team/");
  });

  it("Should navigate to 'Login' when 'Login' is clicked in the menu", () => {
    cy.get(".menu-items").should("not.be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
    cy.contains("a", "Login").click();
    cy.url().should("eq", "http://127.0.0.1:8000/ai-team/login/");
  });

  it("Should navigate to 'FAQs' when 'FAQs' is clicked in the menu", () => {
    cy.get(".menu-items").should("not.be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
    cy.get("[cy-data='faq-link'] a").click();
    cy.wait(6000);
    cy.get(".message-left").should("contain", "I understand that the focus is on empowering individual developers to become significantly more productive with AITeam.");
  });

  it("Should navigate to 'Contact Us' and send an email when we sen the first message", () => {
    cy.get(".menu-items").should("not.be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
    cy.get("[cy-data='contact-link'] a").click();
    cy.wait(6000);
    cy.get(".message-left").last().should("contain", "To contact us");
    cy.get("#userMessage").type("cypresstest.com");
    cy.get(".btn-send").click();
    cy.get(".message-right .message-content").last().should("contain", "cypresstest.com");
    cy.wait(3000)
    cy.get("#userMessage").type("How can AiTeam help me be more productive?{enter}");
    cy.wait(3000)
    cy.get(".message-left").last().should("contain", "AiTeam");
  });

  it("Should navigate to 'Contact Us' and dont send an email when 'Contact Us' is clicked in the menu", () => {
    const message = 'random word'
    cy.get(".menu-items").should("not.be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
    cy.get("[cy-data='contact-link'] a").click();
    cy.wait(6000);
    cy.get(".message-left").last().should("contain", "To contact us");
    cy.get("#userMessage").type(message);
    cy.get(".btn-send").click();
    cy.get(".message-right").last().should("contain", message);
    cy.wait(3000)
    cy.get("#userMessage").type("How can AiTeam help me be more productive?{enter}");
    cy.wait(3000)
    cy.get(".message-left").last().should("contain", "AiTeam");
  });

  it("Should navigate to 'About Us' when 'About Us' is clicked in the menu", () => {
    cy.get(".menu-items").should("not.be.visible");
    cy.get("label[for='hamburgerToggle']").click();
    cy.get(".menu-items").should("be.visible");
    cy.get("[cy-data='about-link'] a").click();
    cy.wait(6000);
    cy.get(".message-left").should("contain", "is a seasoned software engineer with 7 years of experience");
  });

});
