from django.db import models
from django.contrib.auth.models import User

class UserProfile( models.Model ):
    user = models.ForeignKey (User, unique=True, edit_inline=models.TABULAR,
            num_in_admin=1, min_num_in_admin=1, max_num_in_admin=1,
            num_extra_on_change=0)

    about = models.TextField(blank=True, core=True)
    imap_password = models.CharField(maxlength=50)
