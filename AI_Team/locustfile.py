from locust import HttpUser, task, between
import random


class MyUser(HttpUser):
    username_counter = 1
    wait_time = between(2, 5)
    contexts = ["main", "subscription", "panel-admin"]

    @task
    def on_start(self):
        self.username = f"my_username_{self.username_counter}"
        self.username_counter += 1
        self.signup()
        self.reset_password()
        self.login()
        for i in self.contexts:
            self.send_message_and_wait(str(i))
        self.client.get("ai-team/logout/")
    
    def signup(self):
        self.client.post("ai-team/signup/", data={
            "email": "my_email@example.com",
            "username": self.username,
            "password1": "my_password",
            "password2": "my_password"
        })
    
    
    def reset_password(self):
        self.client.post("ai-team/password-reset/", data={
            "username": self.username,
            "email": "my_email@example.com",
            "newpassword": "my_new_password",
            "confirmpassword": "my_new_password"
        })

    
    def login(self):
        response = self.client.get("ai-team/login/")  # Hacer una solicitud GET a la página de inicio de sesión
        csrf_token = response.cookies['csrftoken']  # Obtener el valor del token CSRF de las cookies de la respuesta
        self.client.post("ai-team/login/", data={
            "username": self.username,
            "password": "my_new_password"
        }, headers={"X-CSRFToken": csrf_token})  # Incluir el token CSRF en las cabeceras de la solicitud POST
    
    
    def send_message_and_wait(self, context):
        self.client.get(f"ai-team/chat/{context}/")
        messages = {
        'main':[
            "What are the key features of AITeam?","How can AITeam improve my productivity as a developer?","Can AITeam help me with debugging and writing tests?",
            "How does AITeam generate code?","Does AITeam follow industry best practices?","Can AITeam integrate with my existing workflow?","How quickly can I see productivity improvements with AITeam?",
            "Can AITeam help me refactor my code?"," Does AITeam offer personalized coding recommendations?","How does AITeam learn from my coding style and preferences?"
            "What tools does AITeam provide for debugging and refactoring?","Can AITeam write bug-free code for me?","How can AITeam help me meet deadlines?"
            "Are there any subscription plans for AITeam?","How can I access the Admin panel and create an HTML page with AITeam?"
            ],
        'subscription':[
            "What are the benefits of the Entry Plan?","How does the Entry Plan differ from the Premium Plan?","What analytics features are included in the Entry Plan?",
            "Can you provide more details about the customization options in the Entry Plan?", "What level of support is available in the Entry Plan?","What are the target markets for the Entry Plan?",
            "What are the key features of the Premium Plan?", "How does the Premium Plan compare to the Entry Plan in terms of customization?","What additional features does the Premium Plan offer compared to the Entry Plan?",
            "Is there a limit on data collection in the Premium Plan?","What target markets is the Premium Plan designed for?", "Can you explain the benefits of the Enterprise Plan?",
            "What services are included in the Enterprise Plan?", "Is there a dedicated account manager in the Enterprise Plan?", "How can I pay for the subscription plans?"
            ],
        'panel-admin':[
            "The title of my web page should be 'Tienda de moda online'. This title will appear on the browser tab when visitors access my website. I want it to clearly reflect the focus of my business and attract customers interested in online fashion.",
            "I want the main heading of my page to be 'Descubre las últimas tendencias'. This heading will be the main title of my website and should immediately capture the attention of visitors. I want to convey the idea that my page offers up-to-date information on the latest fashion trends.",
            "The description of my web page is 'Encuentra la mejor selección de ropa y accesorios de moda'. This brief but informative description will appear in search results and help users quickly understand the content of my page. I want to highlight that my site offers a wide range of high-quality fashion products."
            "Some keywords related to my page are 'moda, tienda online, ropa de calidad'. These keywords are important for search engine optimization (SEO) and will help make my page more visible to users interested in fashion and online shopping. I want to ensure that my page appears in relevant search results."
            "When someone visits my page for the first time, I would like to display the message 'Bienvenido a nuestra tienda de moda en línea'. This welcome message will be the first impression that visitors get when accessing my website. I want them to feel welcomed and excited to explore my online store."
            ]
        
        }
        get_context = messages[context]
        message_send = random.choice(get_context)
        csrf_token = self.client.cookies.get(0)
        context_send = str(context)
        message = messages[context_send]
        phase = "user_message"
        url_endpoint = f"ai-team/chat/{context}/"  # Replace "currentContext" with the actual value
        
        form_data = {
            "message": message,
            "phase": phase
        }
        
        response = self.client.post(url_endpoint, data=form_data, headers={"X-CSRFToken": csrf_token})
        
        if response.ok:
            ai_response = response.json()
            # Wait for the response or perform any other necessary actions