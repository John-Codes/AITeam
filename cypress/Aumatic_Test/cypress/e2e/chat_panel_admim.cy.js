describe("Chat Panel Admin tests", () => {
    beforeEach(() => {
      cy.visit("/chat/panel-admin/");
    });
    
    it("Should display the default message", () => {
      const default_message = "In this chat, you'll be able to provide our AI with the essential information to craft your very own AI Chat – a perfect tool to impress your clients, boss, or friends. Here's what we need from you:";
      cy.get(".message-left .message-content").last().should("contain", default_message);
    })

    it("Generate my own site web", () => {
      const title = "Social Media like a power tool";
      const header = "Social Media";
      const navigation_links = "an url to youtube with text youtube, an url to facebook with text facebook, an url to instagram with text instagram";
      const default_message = "I can show you how to use the social media, and how to generate cash";
      cy.get("#userMessage").type(` y want a title ${title}, a header like ${header}, and mi links has to be ${navigation_links}, the default message of mi site is ${default_message}{enter}`);
      cy.wait(9000);
      cy.reload();
      cy.get(".menu-items").should("not.be.visible");
      cy.get("label[for='hamburgerToggle']").click();
      cy.get(".menu-items").should("be.visible");
      cy.contains("a", "My site").click();
      cy.url().should("include", "ai-team/chat/Uptc%253Fto=");      
      cy.get(".menu-items a").should("contain", "My Site");
    })
  
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
  
    it("Should navigate to 'Home' when 'Home' is clicked in the menu", () => {
      cy.get(".menu-items").should("not.be.visible");
      cy.get("label[for='hamburgerToggle']").click();
      cy.get(".menu-items").should("be.visible");
      cy.contains("a", "Home").click();
      cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/chat/main/");
    });

    it("Should navigate to 'Subscripción' when 'Subscripción' is clicked in the menu", () => {
        cy.get(".menu-items").should("not.be.visible");
        cy.get("label[for='hamburgerToggle']").click();
        cy.get(".menu-items").should("be.visible");
        cy.contains("a", "subscriptions").click();
        cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/chat/subscription/");
    });

    it("Should navigate to 'Logout' when 'Logout' is clicked in the menu", () => {
        cy.get(".menu-items").should("not.be.visible");
        cy.get("label[for='hamburgerToggle']").click();
        cy.get(".menu-items").should("be.visible");
        cy.contains("a", "Logout").click();
        cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/chat/login/");
    });
  
});
  