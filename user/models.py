from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from api.utils import validate_image
import uuid

class TimeAt(models.Model):
    created_at = models.DateTimeField(verbose_name="Created At", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="Updated At", auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, password, **extra_fields):
        """ Creates and saves a User with the given password and optional extra fields. """
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        """ Creates and saves a Superuser with the given email and password. """
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    # def update_membership(self, user_id, is_membership):
    #     self.model.objects.filter(id=user_id).update(is_membership=is_membership)


class UserType(models.IntegerChoices):
    INDIVIDUAL = 1,
    ORGANIZATION = 2,


class GenderType(models.IntegerChoices):
    MALE = 1,
    FEMALE = 2,
    OTHER = 3


class GizerType(models.IntegerChoices):
    AUTHOR = 1,
    STUDENT = 2,
    TEACHER = 3,
    SPECIALIST = 4
    PROFESSOR = 5
    RESEARCHER = 6


class OrganizationType(models.IntegerChoices):
    GOVERNMENT_ENTITY = 1,
    NON_GOVERNMENT_ENTITY = 2


LOGIN_TYPE = (
    ("GOOGLE", "GOOGLE"),
    ("APPLE", "APPLE")
)


class OrganizationIndustryType(models.IntegerChoices):
    MINISTRY_OF_FOREIGN_AFFAIRS = 1,
    MINISTRY_OF_INTERIOR_OR_HOME_AFFAIRS = 2
    MINISTRY_OF_FINANCE_OR_TREASURY = 3
    MINISTRY_OF_DEFENSE = 4
    MINISTRY_OF_HEALTH = 5
    MINISTRY_OF_EDUCATION = 6
    MINISTRY_OF_JUSTICE = 7
    MINISTRY_OF_TRANSPORTATION = 8
    MINISTRY_OF_ENVIRONMENT = 9
    MINISTRY_OF_AGRICULTURE = 10
    MINISTRY_OF_CULTURE = 11
    MINISTRY_OF_TRADE_AND_COMMERCE = 12
    MINISTRY_OF_SOCIAL_SERVICES_OR_WELFARE = 13
    MINISTRY_OF_SCIENCE_AND_TECHNOLOGY = 14
    MINISTRY_OF_LABOR_OR_EMPLOYMENT = 15
    MINISTRY_OF_TOURISM = 16
    MINISTRY_OF_COMMUNICATION_OR_INFORMATION_TECHNOLOGY = 17
    MINISTRY_OF_HOUSING_AND_URBAN_DEVELOPMENT = 18
    MINISTRY_OF_YOUTH_AND_SPORTS = 19
    INDEPENDENT_REGULATORY_AUTHORITIES = 20
    LAW_ENFORCEMENT_AND_SECURITY_AGENCIES = 21
    PUBLIC_HEALTH_AND_SAFETY_AGENCIES = 22
    ENVIRONMENTAL_PROTECTION_AGENCIES = 23
    TRANSPORTATION_AND_INFRASTRUCTURE_DEPARTMENTS = 24
    EDUCATION_BOARDS_AND_AUTHORITIES = 25
    LABOR_AND_EMPLOYMENT_DEPARTMENTS = 26
    CULTURAL_AND_ARTS_ORGANIZATIONS = 27
    STATISTICAL_AND_DATA_AGENCIES = 28
    FOREIGN_AFFAIRS_AND_DIPLOMATIC_MISSIONS = 29
    FINANCIAL_AND_ECONOMIC_AGENCIES = 30
    SOCIAL_SERVICES_AND_WELFARE_DEPARTMENTS = 31
    EMERGENCY_SERVICES_AND_DESASTER_MANAGEMENT_SERVICES = 32
    SCIENCE_AND_RESEARCH_INSTITUTES = 33
    TECHNOLOGIES_AND_INNOVATION_AUTHORITIES = 34
    COMMUNICATIONS_AND_INFORMATION_TECHNOLOGY_AUTHORITIES = 35
    AGRICULTURAL_AND_RURAL_DEVELOPMENT_DEPARTMENTS = 36
    TRADE_AND_COMMERCE_AUTHORITIES = 37
    HOUSING_AND_URBAN_DEVELOPMENT_DEPARTMENTS = 38
    YOUTH_AND_SPORTS_ORGANIZATIONS = 39
    ECONOMIC_DEVELOPMENT_AND_INVESTMENT_AGENCIES = 40
    AGRICULTURE = 41
    AUTOMOTIVE = 42
    BANKING_AND_FINANCE = 43
    CHEMICALS = 44
    CONSTRUCTION_AND_REAL_ESTATE = 45
    EDUCATION_AND_TRAINING = 46
    ENERGY = 47
    ENTERTAINMENT_AND_MEDIA = 48
    ENVIRONMENTAL_SERVICES = 49
    FOOD_AND_BEVERAGE = 50
    GOVERNMENT_AND_PUBLIC_ADMINISTRATION = 51
    HEALTH_AND_PHARMACEUTICALS = 52
    INFORMATION_TECHNOLOGY = 53
    MANUFACTURING = 54
    MINING_AND_METALS = 55
    NONPROFIT_AND_NGOS = 56
    RETAIL = 57
    TELECOMMUNICATIONS = 58
    TEXTILES_AND_APPAREL = 59
    TRANSPORTATION_AND_LOGISTICS = 60
    TRAVEL_AND_TOURISM = 61


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True, max_length=120)
    first_name = models.CharField(max_length=100, default=None, null=True)
    last_name = models.CharField(max_length=100, default=None, null=True)
    phone_number = PhoneNumberField(unique=True, null=True)
    user_type = models.IntegerField(choices=UserType.choices, help_text=UserType.choices, blank=True, null=True)
    gizer_subtype = models.IntegerField(choices=GizerType.choices, help_text=GizerType.choices, blank=True, null=True)
    gizer_name = models.CharField(max_length=120, null=True, blank=True)
    speciality = models.CharField(max_length=120, null=True, blank=True)
    organization_name = models.CharField(max_length=120, null=True, blank=True)
    organization_type = models.IntegerField(choices=OrganizationType.choices, help_text=OrganizationType.choices,
                                            blank=True, null=True)
    organization_industry = models.IntegerField(choices=OrganizationIndustryType.choices,
                                                help_text=OrganizationIndustryType.choices,
                                                blank=True, null=True)
    verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    login_type = models.CharField(choices=LOGIN_TYPE, max_length=20, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    giz_verification = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number']


class Country(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=255, unique=True, primary_key=True)
    phone_code = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Language(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.id} | {self.name}"


class Currency(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id} | {self.name}"


class UserProfile(TimeAt):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to="picture", null=True, blank=True, validators=[validate_image])
    cover_picture = models.ImageField(upload_to="cover_picture", null=True, blank=True, validators=[validate_image])
    bio = models.TextField(max_length=160, blank=True, null=True)
    gender = models.IntegerField(choices=GenderType.choices, help_text=GenderType.choices, blank=True, null=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True,  on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, null=True, blank=True,  on_delete=models.CASCADE)
    language = models.ForeignKey(Language, null=True, blank=True,  on_delete=models.CASCADE)
    twitter_link = models.URLField(blank=True, null=True)
    linkedin_link = models.URLField(blank=True, null=True)
    website_link = models.URLField(blank=True, null=True)
    facebook_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)
    last_seen = models.DateTimeField(auto_now=True, db_index=True)

    def __str__(self):
        return '{} - {}'.format(self.pk, self.user)


class DeviceDetails(TimeAt):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    model = models.CharField(max_length=255)

    def __str__(self):
        return '{}'.format(self.pk)


class FirebaseAuth(TimeAt):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    uid = models.CharField(max_length=255, unique=True)


class UserVerificationStatus(models.IntegerChoices):
    PENDING = 1,
    ACCEPTED = 2
    REJECTED = 3

class UserVerification(TimeAt):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    passport = models.ImageField(upload_to="user_passport", validators=[validate_image])
    profile_picture = models.ImageField (upload_to="profile_picture", validators=[validate_image])
    header_image = models.ImageField(upload_to="header_image", validators=[validate_image])
    bio = models.TextField()
    letter = models.FileField(upload_to='letter', null=True, validators=[validate_image])
    status = models.IntegerField(choices=UserVerificationStatus.choices,
                                                help_text=UserVerificationStatus.choices,
                                                default=1)