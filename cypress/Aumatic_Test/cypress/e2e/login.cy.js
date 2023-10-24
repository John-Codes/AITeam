describe("Login Page Tests", () => {
  beforeEach(() => {
    // Antes de cada prueba, visita la página de inicio de sesión
    cy.visit("/login/");
  });

  it("Should successfully log in when 'Enter' button is clicked", () => {
    // Ingresa las credenciales de prueba
    cy.get("#id_username").type("efexium");
    cy.get("#id_password").type("$@dm1nsup34()s3pr4ef3x");

    // Haz clic en el botón 'Enter'
    cy.get(".btn-dark-submit").click();

    // Verifica que se haya iniciado sesión correctamente
    // Puedes utilizar aserciones para verificar que se muestra el contenido de la página a la que rediriges después del inicio de sesión
    cy.contains("efexzium =$=");
  });

  it("Should navigate to the registration page when 'Create account' link is clicked", () => {
    // Haz clic en el enlace 'Create account'
    cy.contains("Create account").click();

    // Verifica que la página redirija a la página de registro
    cy.url().should("include", "/aiteam/signup/");
  });

  it("Should navigate to the password reset page when 'Reset password' link is clicked", () => {
    // Haz clic en el enlace 'Reset password'
    cy.contains("Reset password").click();

    // Verifica que la página redirija a la página de restablecimiento de contraseña
    cy.url().should("include", "/aiteam/password_reset/");
  });

});
