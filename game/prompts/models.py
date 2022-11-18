from django.db import models

# Create your models here.

category_choices = [
    ("Movie Titles", "Movie Titles"),
    ("Song Titles", "Song Titles"),
    ("Pop Culture", "Pop Culture"),
    ("Miscellaneous", "Miscellaneous"),
    ("Idioms", "Idioms"),
    ("Places/Attractions", "Places/Attractions"),
    ("Toys and Games", "Toys and Games"),
]


class Prompt(models.Model):
    """
    Model for storing prompts that a user will attempt to communicate via only emojis.
    """

    message = models.CharField(max_length=500)
    category = models.CharField(
        max_length=50, choices=category_choices, null=True, blank=True
    )
    hints = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return_dict = {
            "message": self.message,
            "category": self.category,
        }
        return str(return_dict)


class PromptClue(models.Model):
    room_id = models.IntegerField()
    leader_id = models.IntegerField()
    prompt = models.ForeignKey(Prompt, on_delete=models.PROTECT)
    clue = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "room_id",
            "leader_id",
            "prompt",
            "clue",
        )


class ClueGuess(models.Model):
    room_id = models.IntegerField()
    roommember_id = models.IntegerField()
    clue = models.CharField(max_length=50)
    guess = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
