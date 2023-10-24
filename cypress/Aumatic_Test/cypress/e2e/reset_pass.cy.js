describe("Password Reset Page Tests", () => {
  beforeEach(() => {
    // Antes de cada prueba, visita la página de restablecimiento de contraseña
    cy.visit("/password-reset/");
  });

  it("Should successfully reset password", () => {
    // Ingresa los datos de restablecimiento de contraseña de prueba
    cy.get("#username").type("cliente");
    cy.get("#email").type("ejemplo@user.com");
    cy.get("#newpassword").type("minuevacontraseñasegura");
    cy.get("#confirmpassword").type("minuevacontraseñasegura");

    // Haz clic en el botón 'Change Password'
    cy.get(".btn-dark-submit").click();

    // Verifica que la contraseña se haya restablecido correctamente
    // Puedes utilizar aserciones para verificar que se muestra el contenido de la página a la que rediriges después del restablecimiento de contraseña
    cy.contains("Password changed successfully."); // Cambia el texto según tu página de destino después del restablecimiento de contraseña
    cy.get(".alert button.btn-close").should("exist");
    cy.get(".alert button.btn-close").click();

    //  Verifica que el mensaje de éxito ya no esté presente
    cy.contains("Password changed successfully.").should("not.exist");
  });

  it("Should navigate to the login page when 'Log in' link is clicked", () => {
    // Haz clic en el enlace 'Log in'
    cy.contains("Log in").click();

    // Verifica que la página redirija a la página de inicio de sesión
    cy.url().should("eq", "https://aiteam-app-vpvo8.ondigitalocean.app/ai-team/login/");
  });

  // Agrega más pruebas si es necesario...
});
