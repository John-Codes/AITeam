from django.db import models

class UserQuestion(models.Model):
    question_text = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text