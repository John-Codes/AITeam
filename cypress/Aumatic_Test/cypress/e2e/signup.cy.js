describe("Signup Page Tests", () => {
  beforeEach(() => {
    // Antes de cada prueba, visita la página de registro
    cy.visit("http://127.0.0.1:8000/aiteam/signup/");
  });

  it("Should successfully register a new account", () => {
    // Ingresa los datos de registro de prueba
    cy.get("#id_email").type("example@gmail.com");
    cy.get("#id_username").type("cliente21");
    cy.get("#id_password1").type("mypassis684securiyrtfdf");
    cy.get("#id_password2").type("mypassis684securiyrtfdf");

    // Haz clic en el botón 'Register'
    cy.get(".btn-dark-submit").click();

    // Verifica que se haya registrado correctamente
    // Puedes utilizar aserciones para verificar que se muestra el contenido de la página a la que rediriges después del registro
    cy.contains("Log In"); // Cambia el texto según tu página de destino después del registro
  });

  it("Should navigate to the login page when 'Log in' link is clicked", () => {
    // Haz clic en el enlace 'Log in'
    cy.contains("Log in").click();

    // Verifica que la página redirija a la página de inicio de sesión
    cy.url().should("include", "/aiteam/login/");
  });

  // Agrega más pruebas si es necesario...
});
