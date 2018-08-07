import os

from django.db import models
# from django.contrib.auth.hashers import check_password, set_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.core.files.storage import FileSystemStorage


from BMB_Registration.listfield import ListField
from BCM.settings import MEDIA_ROOT


TSHIRT_SIZES = (('XS','EXTRA-SMALL'), ('S' , 'SMALL'),
                ('M', 'MEDIUM'), ('L', 'LARGE'),
                ('XL', 'EXTRA-LARGE'), ('XXL', 'XX-LARGE'),
                ('XXXL', 'XXXL'), ('None','None'))

BOOL         = (('yes', 'yes'), ('no', 'no'))

GENDER       = (('male', 'male'), ('female', 'female'))

PRESENTATION = (('poster', 'poster'), ('talk', 'talk'),
                ('decline', 'decline'))

POSITION     = (('student', 'student'), ('postdoc', 'postdoc'),
                ('faculty', 'faculty'), ('staff', 'staff'))

ATTENDANCE   = (('both', 'both'), ('thursday', 'thursday'),
                ('friday', 'friday')
)

class PI(models.Model):
    first_name = models.CharField(max_length=30)
    last_name  = models.CharField(max_length=30)

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)

    class Meta:
        verbose_name        = 'PI'
        verbose_name_plural = 'PIs'


class Department(models.Model):

    name = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return '{}'.format(self.name)

class User(models.Model):
    first_name      = models.CharField(max_length=30)
    last_name       = models.CharField(max_length=30)
    gender          = models.CharField(choices=GENDER, max_length=6, default='')
    department      = models.ForeignKey(Department)
    position        = models.CharField(choices=POSITION, max_length=7, default='')
    password        = models.CharField(max_length=100)
    email           = models.EmailField(blank=False, unique=True)
    date_registered = models.DateTimeField(auto_now_add=True)
    lab             = models.ForeignKey(PI, blank=True)
    lab_department  = models.ForeignKey(Department)
    shirt_size      = models.CharField(choices=TSHIRT_SIZES, max_length=4)
    presentation    = models.CharField(choices=PRESENTATION, default='decline', max_length=7, help_text='Years 3 and above must present a poster.')
    funding_source  = models.CharField(max_length=10)
    stay_at_hotel   = models.CharField(choices=BOOL, default='yes', max_length=3)
    share_room      = models.CharField(choices=BOOL, default='yes', max_length=3)
    roommate_pref   = models.CharField(max_length=100, blank=True, help_text='Optional')
    vegetarian      = models.CharField(choices=BOOL, default='no', max_length=3)
    rank_posters    = models.CharField(blank=True, null=True, max_length=30)
    detailed_posters =  models.CharField(blank=True, null=True, max_length=30)
    last_login      = models.DateTimeField(blank=True, null=True)
    attendance      = models.CharField(choices=ATTENDANCE, default='both', max_length=20)


    list_display =  ('last_name', 'first_name', 'gender',
                     'department', 'lab', 'lab_department','position', 'email',
                     'date_registered', 'shirt_size', 'presentation',
                     'funding_source', 'stay_at_hotel', 'share_room',
                     'roommate_pref', 'vegetarian'
                    )
    class Meta:
        ordering = ('-last_name', '-first_name')

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, setter)



class Variable(models.Model):
    variable_name  = models.CharField(max_length=50)
    variable_value = models.CharField(max_length=300)


    def __str__(self):
        return '%s = %s' % (self.variable_name, self.variable_value)


class Submission(models.Model):

    user          = models.ForeignKey(User)
    # submission_type  = models.ForeignKey('User.presentation')
    title         = models.CharField(max_length=500)
    presenter     = models.CharField(max_length=500, blank=True, default='')
    authors       = models.CharField(max_length=500, blank=True, default='')
    final_author  = models.CharField(max_length=500, blank=True, default='')
    PI            = models.ForeignKey(PI, blank=True, null=True)
    abstract      = models.TextField(max_length=(9*360),
                                     help_text="""For superscript, enter "$^{text}$".
                                     For subscript, enter "$_{text}$".
                                     For italics, enter "\\textit{text}".
                                     For bold, enter "\\textbf{text}".
                                     Greek letters can be entered directly.
                                     """
    )
    poster_number = models.IntegerField(blank=True, null=True, unique=True)
    scores        = models.CharField(blank=True, null=True, max_length=30)
    avg_score     = models.FloatField(blank=True, null=True)
    rank          = models.IntegerField(blank=True, null=True)
    rank_judges   = models.CharField(blank=True, null=True, max_length=30)
    detailed_judges =  models.CharField(blank=True, null=True, max_length=30)
    assigned_ranks = models.IntegerField(blank=True, null=True)
    assigned_detailed = models.IntegerField(blank=True, null=True)

    list_display  = ('user', 'title', 'authors', 'PI', 'poster_number')

    rank.list_lookup_range = ( (None, ('All')),
                               ([0, 8], '0-8'),
                               ([9, 16], '9-16'),
                               ([17, 24], '17-24'),
                               ([25, 32], '25-32'),
                               ([33, None], '33+'),
                               )
    def __str__(self):
        # return '{}\n{} {}'.format(self.title, self.user, self.authors)
        if self.poster_number:
            return '{} : {}'.format(self.poster_number, self.user)
        else:
            return 'Talk : {}'.format(self.user)


    class Meta:
        ordering = ('-avg_score',)

    @property
    def presentation(self):
        return self.user.presentation

class PosterRank(models.Model):

    rank_set        = models.PositiveSmallIntegerField()
    rank            = models.PositiveSmallIntegerField()
    poster_number   = models.ForeignKey(Submission, to_field='poster_number',
                                        on_delete=models.CASCADE
    )

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'uploads/{0}_{1}/{2}'.format(instance.user.last_name, instance.user.first_name, filename)


class Upload(models.Model):

    user = models.ForeignKey(User)
    upload = models.FileField(upload_to=user_directory_path)

    def __str__(self):
        return '{2}'.format(self.user.last_name, self.user.first_name, self.upload)

    # def file_link(self):
    #     if self.upload:
    #         return "<a href='%s'>download</a>" % (self.upload.url,)
    #     else:
    #         return "No attachment"

    # file_link.allow_tags = True
