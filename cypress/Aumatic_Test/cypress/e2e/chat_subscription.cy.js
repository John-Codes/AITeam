describe("Chat Subscripcion tests", () => {
    beforeEach(() => {
      cy.visit("/chat/subscription/");
    });
    
    it("Should display the default message", () => {
      cy.get(".message-left .message-content").last().should("contain", "Information about your subscription:");
      cy.contains("a", "Subscription").click();
      cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/chat/subs-page/");      
    })

    it("Has a cancel button", () => {
    const message = "Are you sure you want to cancel your subscription?";
      cy.get(".message-left .message-content").last().should("contain", "Information about your subscription:");
      cy.contains("button", "Cancel Subscription").click
      cy.get(".message-left .message-content").last().should("contain", message);
      cy.get("#userMessage").type('no');
      cy.get(".message-right .message-content").last().should("contain", 'no');
    })

    it("Should send a message when Enter key is pressed", () => {
      const message = "What are the subscriptions that do you offer";
      cy.get("#userMessage").type(`${message}{enter}`);
      cy.get(".message-right .message-content").last().should("contain", message);
      cy.wait(9000);
      cy.get(".chat-body").last();
    });
  
    it("Should send a message when the 'Send' button is clicked", () => {
      const message = "i am a software engineer, which plan is better for me";
      cy.get("#userMessage").type(message);
      cy.get(".btn-send").click();
      cy.get(".message-right .message-content").last().should("contain", message);
      cy.wait(9000);
      cy.get(".message-left").last();
      cy.get("#userMessage").type(message);
      cy.get(".btn-send").click();
      cy.get(".message-right .message-content").last().should("contain", message);
      cy.wait(9000);
      cy.get(".message-left").last();
    });
  
    it("Should clear the input after sending a message", () => {
      const message = "i am a software engineer, which plan is better for me";
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
  
    it("Should send a message 'What are the plans' when Enter key is pressed", () => {
      const message = "What are the plans";
      cy.get("#userMessage").type(`${message}{enter}`);
      cy.get(".message-right .message-content").last().should("contain", message);
    });
  
    it("Should navigate to 'Home' when 'Home' is clicked in the menu", () => {
      cy.get(".menu-items").should("not.be.visible");
      cy.get("label[for='hamburgerToggle']").click();
      cy.get(".menu-items").should("be.visible");
      cy.contains("a", "Home").click();
      cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/chat/main/");
    });

    it("Should navigate to 'Panel Admin' when 'Panel Admin' is clicked in the menu", () => {
        cy.get(".menu-items").should("not.be.visible");
        cy.get("label[for='hamburgerToggle']").click();
        cy.get(".menu-items").should("be.visible");
        cy.contains("a", "Admin Panel").click();
        cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/chat/panel-admin/");
    });

    it("Should navigate to 'Logout' when 'Logout' is clicked in the menu", () => {
        cy.get(".menu-items").should("not.be.visible");
        cy.get("label[for='hamburgerToggle']").click();
        cy.get(".menu-items").should("be.visible");
        cy.contains("a", "Logout").click();
        cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/chat/login/");
    });
  
});
  