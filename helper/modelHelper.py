from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

######################## Regex ###############
Alphanumeric_Regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
Number_Regex = '^[0-9]$'
Password_Regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]+$'

Email_Validator = RegexValidator(EMAIL_REGEX, _('Enter a valid email address.'))
Number_Validator = RegexValidator(Number_Regex, _('Only Number  are allowed.'))
Alphanumeric_Validator = RegexValidator(Alphanumeric_Regex, _('Only alphanumeric characters are allowed.'))
Password_Validator = RegexValidator(Password_Regex, _('password must contain are allowed.'))
######################## Months ###############
Months_Helper = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'),
                 ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12'))
DurationUnit = (('Hours', _('Hours')), ('Minutes', _('Minutes')), ('None', 'None'),)
DurationTime = ((10, 10), (15, 15), (30, 30), (60, 60),)
WorkingDay = (('Saturday', _('Saturday')), ('Sunday', _('Sunday')), ('Monday', _('Monday')), ('Tuesday', _('Tuesday')),
              ('Wednesday', _('Wednesday')), ('Thursday', _('Thursday')), ('Friday', _('Friday')),)
# DayType = (('Morning', _('Morning')), ('Evening', _('Evening')), ('All', _('All Day')),('Holiday', _('Holiday')),)
TimeSlotType = (('Morning', _('Morning')), ('Evening', _('Evening')), ('All', _('All Day')), ('Holiday', _('Holiday')))
######################## Status ###############
Soft_Delete = ((True, "Soft Deleted"), (False, "Not Deleted"))
Genesis_Block = ((True, "Is a Genesis Block."), (False, "Is not a Genesis Block."),)
Notice_Status = ((True, "Send Notice Now"), (False, "Don't Send Notice Now"),)
Importance_Status = ((1, "Critical"), (2, "Very Important"), (3, "Important"))
Active_Status = (('Active', _('Active')), ('Archive', _('Archive')), ('Inactive', _('Inactive')),)
Waiting_Status = (('Active', _('Active')), ('Waiting', _('Waiting for activation')), ('Inactive', _('Inactive')),)
Busy_Status = (('Busy', _('Busy')), ('Free', _('Free')), ('Away', _('Away')), ('Offline', _('Offline')),)
Public_Status = (('Yes', _('Yes')), ('NO', _('NO')),)
Publish_Status = (('Published', _('Published')), ('Scheduled', _('Scheduled')), ('Inactive', _('Inactive')),)
WALLET_STATUS = (('Create', _('Create')), ('Login', _('Login')), ('Logout', _('Logout')), ('Suspend', _('Suspend')),)
Signin_Type = (('NeedActive', _('Need Active')), ('NotNeedActive', _('Not Need Active')), ('Paid', _('Paid')))
AUTH_PROVIDERS = {'facebook': 'facebook', 'google': 'google', 'twitter': 'twitter', 'email': 'email'}
Social_Providers = (('facebook', 'facebook'), ('twitter', 'twitter'), ('instagram', 'instagram'),
                    ('linkedIn ', 'linkedIn'), ('behance ', 'behance'), ('youtube ', 'youtube'), ('other ', 'other'),)
Friend_Request_Status = (('NOREQUEST', 'NOREQUEST'), ('SENT', 'SENT'), ('PENDING', 'PENDING'), ('APPROVED', 'APPROVED'),
                         ('DECLINE', 'DECLINE'))
Follower_Type = (('FOLLOWER', _('FOLLOWER')), ('FOLLOWING', _('FOLLOWING')))
Otp_Type = (('App', _("App")), ('Email', _("Email")), ('WhatsApp', _("WhatsApp")), ('SMS', _("SMS")),
            ('None', _("None")),)

Email_Type = (('Personal', _('Personal')), ('Work', _('Work')), ('Other', _('Other')))
Email_status = (('Read', _('Read')), ('Unread', _('Unread')), ('Archive', _('Archive')), ('Trash', _('Trash')),
                ('Spam', _('Spam')), ('Important', _('Important')), ('Starred', _('Starred')), ('Draft', _('Draft')),
                ('Sent', _('Sent')), ('Scheduled', _('Scheduled')), ('Inactive', _('Inactive')),)
Attendees_History_Type = (('CheckIn', _('CheckIn')), ('CheckOut', _('CheckOut')), ('Break', _('Break')),
                          ('Leave', _('Leave')), ('Absent', _('Absent')), ('Early', _('Early')),
                          ('NotChecked', _('Not Checked')))
################### FRONTEND TEMPLATES #############################
BACKEND_TEMPLATES = (('good', 'good'), ('multikart', 'multikart'), ('kundol', 'kundol'),)
MAINTENANCE_TEMPLATES = (('creasoon', 'creasoon'), ('mountain', 'mountain'), ('landio', 'landio'),)
FRONTEND_TEMPLATES = (('mountain', 'mountain'), ('kofejob', 'kofejob'),('downtown', 'downtown'),

                      ('creasoon', 'creasoon'),)

Home_Index = (('Home', 'Home'), ('Home2', 'Home2'), ('Home3', 'Home3'), ('Home4', 'Home4'), ('Home5', 'Home5'),)
Site_Type = (('Frontend', 'Frontend'), ('Backend', 'Backend'), ('Maintenance', 'Maintenance'),)
############### Country List ###############

Country_List = (('Afghanistan', _('Afghanistan')), ('Albania', _('Albania')), ('Algeria', _('Algeria')),
                ('American Samoa', _('American Samoa')), ('Andorra', _('Andorra')), ('Angola', _('Angola')),
                ('Anguilla', _('Anguilla')), ('Antarctica', _('Antarctica')),
                ('Antigua and Barbuda', _('Antigua and Barbuda')), ('Argentina', _('Argentina')),
                ('Armenia', _('Armenia')), ('Aruba', _('Aruba')), ('Australia', _('Australia')),
                ('Austria', _('Austria')), ('Azerbaijan', _('Azerbaijan')), ('Bahamas', _('Bahamas')),
                ('Bahrain', _('Bahrain')), ('Bangladesh', _('Bangladesh')), ('Barbados', _('Barbados')),
                ('Belarus', _('Belarus')), ('Belgium', _('Belgium')), ('Belize', _('Belize')), ('Benin', _('Benin')),
                ('Bermuda', _('Bermuda')), ('Bhutan', _('Bhutan')), ('Bolivia', _('Bolivia')),
                ('Bosnia and Herzegovina', _('Bosnia and Herzegovina')), ('Botswana', _('Botswana')),
                ('Bouvet Island', _('Bouvet Island')), ('Brazil', _('Brazil')),
                ('British Indian Ocean Territory', _('British Indian Ocean Territory')),
                ('Brunei Darussalam', _('Brunei Darussalam')), ('Bulgaria', _('Bulgaria')),
                ('Burkina Faso', _('Burkina Faso')), ('Burundi', _('Burundi')), ('Cambodia', _('Cambodia')),
                ('Cameroon', _('Cameroon')), ('Canada', _('Canada')), ('Cape Verde', _('Cape Verde')),
                ('Cayman Islands', _('Cayman Islands')), ('Central African Republic', _('Central African Republic')),
                ('Chad', _('Chad')), ('Chile', _('Chile')), ('China', _('China')),
                ('Christmas Island', _('Christmas Island')), ('Cocos (Keeling) Islands', _('Cocos (Keeling) Islands')),
                ('Colombia', _('Colombia')), ('Comoros', _('Comoros')), ('Congo', _('Congo')),
                ('Congo, The Democratic Republic of The', _('Congo, The Democratic Republic of The')),
                ('Cook Islands', _('Cook Islands')), ('Costa Rica', _('Costa Rica')),
                ('Cote Divoire', _('Cote Divoire')), ('Croatia', _('Croatia')), ('Cuba', _('Cuba')),
                ('Cyprus', _('Cyprus')), ('Czech Republic', _('Czech Republic')), ('Denmark', _('Denmark')),
                ('Djibouti', _('Djibouti')), ('Dominica', _('Dominica')),
                ('Dominican Republic', _('Dominican Republic')), ('Ecuador', _('Ecuador')), ('Egypt', _('Egypt')),
                ('El Salvador', _('El Salvador')), ('Equatorial Guinea', _('Equatorial Guinea')),
                ('Eritrea', _('Eritrea')), ('Estonia', _('Estonia')), ('Ethiopia', _('Ethiopia')),
                ('Falkland Islands (Malvinas)', _('Falkland Islands (Malvinas)')),
                ('Faroe Islands', _('Faroe Islands')), ('Fiji', _('Fiji')), ('Finland', _('Finland')),
                ('France', _('France')), ('French Guiana', _('French Guiana')),
                ('French Polynesia', _('French Polynesia')),
                ('French Southern Territories', _('French Southern Territories')), ('Gabon', _('Gabon')),
                ('Gambia', _('Gambia')), ('Georgia', _('Georgia')), ('Germany', _('Germany')), ('Ghana', _('Ghana')),
                ('Gibraltar', _('Gibraltar')), ('Greece', _('Greece')), ('Greenland', _('Greenland')),
                ('Grenada', _('Grenada')), ('Guadeloupe', _('Guadeloupe')), ('Guam', _('Guam')),
                ('Guatemala', _('Guatemala')), ('Guinea', _('Guinea')), ('Guinea-bissau', _('Guinea-bissau')),
                ('Guyana', _('Guyana')), ('Haiti', _('Haiti')),
                ('Heard Island and Mcdonald Islands', _('Heard Island and Mcdonald Islands')),
                ('Holy See (Vatican City State)', _('Holy See (Vatican City State)')), ('Honduras', _('Honduras')),
                ('Hong Kong', _('Hong Kong')), ('Hungary', _('Hungary')), ('Iceland', _('Iceland')),
                ('India', _('India')), ('Indonesia', _('Indonesia')),
                ('Iran, Islamic Republic of', _('Iran, Islamic Republic of')), ('Iraq', _('Iraq')),
                ('Ireland', _('Ireland')), ('Italy', _('Italy')), ('Jamaica', _('Jamaica')), ('Ireland', _('Ireland')),
                ('Japan', _('Japan')), ('Jordan', _('Jordan')), ('Kazakhstan', _('Kazakhstan')), ('Kenya', _('Kenya')),
                ('Kiribati', _('Kiribati')),
                ('Korea, Democratic Peoples Republic of', _('Korea, Democratic Peoples Republic of')),
                ('Korea, Republic of', _('Korea, Republic of')), ('Kuwait', _('Kuwait')),
                ('Kyrgyzstan', _('Kyrgyzstan')),
                ('Lao Peoples Democratic Republic', _('Lao Peoples Democratic Republic')), ('Latvia', _('Latvia')),
                ('Lebanon', _('Lebanon')), ('Lesotho', _('Lesotho')), ('Liberia', _('Liberia')),
                ('Libyan Arab Jamahiriya', _('Libyan Arab Jamahiriya')), ('Liechtenstein', _('Liechtenstein')),
                ('Lithuania', _('Lithuania')), ('Luxembourg', _('Luxembourg')), ('Macao', _('Macao')),
                ('Macedonia, The Former Yugoslav Republic of', _('Macedonia, The Former Yugoslav Republic of')),
                ('Madagascar', _('Madagascar')), ('Malawi', _('Malawi')), ('Malaysia', _('Malaysia')),
                ('Maldives', _('Maldives')), ('Mali', _('Mali')), ('Malta', _('Malta')),
                ('Marshall Islands', _('Marshall Islands')), ('Martinique', _('Martinique')),
                ('Mauritania', _('Mauritania')), ('Mauritius', _('Mauritius')), ('Mayotte', _('Mayotte')),
                ('Mexico', _('Mexico')), ('Micronesia, Federated States of', _('Micronesia, Federated States of')),
                ('Moldova, Republic of', _('Moldova, Republic of')), ('Monaco', _('Monaco')),
                ('Mongolia', _('Mongolia')), ('Montserrat', _('Montserrat')), ('Morocco', _('Morocco')),
                ('Mozambique', _('Mozambique')), ('Myanmar', _('Myanmar')), ('Namibia', _('Namibia')),
                ('Nauru', _('Nauru')), ('Nepal', _('Nepal')), ('Netherlands', _('Netherlands')),
                ('Netherlands Antilles', _('Netherlands Antilles')), ('New Caledonia', _('New Caledonia')),
                ('New Zealand', _('New Zealand')), ('Nicaragua', _('Nicaragua')), ('Niger', _('Niger')),
                ('Nigeria', _('Nigeria')), ('Niue', _('Niue')), ('Norfolk Island', _('Norfolk Island')),
                ('Northern Mariana Islands', _('Northern Mariana Islands')), ('Norway', _('Norway')),
                ('Oman', _('Oman')), ('Pakistan', _('Pakistan')), ('Palau', _('Palau')),
                ('Palestinian Territory, Occupied', _('Palestinian Territory, Occupied')), ('Panama', _('Panama')),
                ('Papua New Guinea', _('Papua New Guinea')), ('Paraguay', _('Paraguay')), ('Peru', _('Peru')),
                ('Philippines', _('Philippines')), ('Pitcairn', _('Pitcairn')), ('Poland', _('Poland')),
                ('Portugal', _('Portugal')), ('Puerto Rico', _('Puerto Rico')), ('Qatar', _('Qatar')),
                ('Reunion', _('Reunion')), ('Romania', _('Romania')), ('Russian Federation', _('Russian Federation')),
                ('Rwanda', _('Rwanda')), ('Saint Helena', _('Saint Helena')),
                ('Saint Kitts and Nevis', _('Saint Kitts and Nevis')), ('Saint Lucia', _('Saint Lucia')),
                ('Saint Pierre and Miquelon', _('Saint Pierre and Miquelon')),
                ('Saint Vincent and The Grenadines', _('Saint Vincent and The Grenadines')), ('Samoa', _('Samoa')),
                ('San Marino', _('San Marino')), ('Sao Tome and Principe', _('Sao Tome and Principe')),
                ('Saudi Arabia', _('Saudi Arabia')), ('Senegal', _('Senegal')),
                ('Serbia and Montenegro', _('Serbia and Montenegro')), ('Seychelles', _('Seychelles')),
                ('Sierra Leone', _('Sierra Leone')), ('Singapore', _('Singapore')), ('Slovakia', _('Slovakia')),
                ('Slovenia', _('Slovenia')), ('Solomon Islands', _('Solomon Islands')), ('Somalia', _('Somalia')),
                ('South Africa', _('South Africa')),
                ('South Georgia and The South Sandwich Islands', _('South Georgia and The South Sandwich Islands')),
                ('Spain', _('Spain')), ('Sri Lanka', _('Sri Lanka')), ('Sudan', _('Sudan')),
                ('Suriname', _('Suriname')), ('Svalbard and Jan Mayen', _('Svalbard and Jan Mayen')),
                ('Swaziland', _('Swaziland')), ('Sweden', _('Sweden')), ('Switzerland', _('Switzerland')),
                ('Syrian Arab Republic', _('Syrian Arab Republic')),
                ('Taiwan, Province of China', _('Taiwan, Province of China')), ('Tajikistan', _('Tajikistan')),
                ('Tanzania, United Republic of', _('Tanzania, United Republic of')), ('Thailand', _('Thailand')),
                ('Timor-leste', _('Timor-leste')), ('Togo', _('Togo')), ('Tokelau', _('Tokelau')),
                ('Tonga', _('Tonga')), ('Trinidad and Tobago', _('Trinidad and Tobago')), ('Tunisia', _('Tunisia')),
                ('Turkmenistan', _('Turkmenistan')), ('Tuvalu', _('Tuvalu')), ('Uganda', _('Uganda')),
                ('Ukraine', _('Ukraine')), ('United Kingdom', _('United Kingdom')),
                ('United States', _('United States')), ('United Arab Emirates', _('United Arab Emirates')),
                ('Uruguay', _('Uruguay')), ('Uzbekistan', _('Uzbekistan')), ('Vanuatu', _('Vanuatu')),
                ('Venezuela', _('Venezuela')), ('Viet Nam', _('Viet Nam')),
                ('Virgin Islands, British', _('Virgin Islands, British')),
                ('Virgin Islands, U.S.', _('Virgin Islands, U.S.')), ('Wallis and Futuna', _('Wallis and Futuna')),
                ('Western Sahara', _('Western Sahara')), ('Yemen', _('Yemen')), ('Zambia', _('Zambia')),
                ('Zimbabwe', _('Zimbabwe')),)
Flag_Emoji = (('1', '🇦🇫'), ('🇦🇽', '🇦🇽'), ('🇦🇱', '🇦🇱'), ('🇩🇿', '🇩🇿'), ('🇦🇸', '🇦🇸'), ('🇦🇩', '🇦🇩'), ('🇦🇴', '🇦🇴'),
              ('🇦🇮', '🇦🇮'), ('🇦🇶', '🇦🇶'), ('🇦🇬', '🇦🇬'), ('🇦🇷', '🇦🇷'), ('🇦🇲', '🇦🇲'), ('🇦🇼', '🇦🇼'), ('🇦🇺', '🇦🇺'),
              ('🇦🇹', '🇦🇹'), ('🇦🇿', '🇦🇿'), ('🇧🇸', '🇧🇸'), ('🇧🇭', '🇧🇭'), ('🇧🇩', '🇧🇩'), ('🇧🇧', '🇧🇧'), ('🇧🇾', '🇧🇾'),
              ('🇧🇪', '🇧🇪'), ('🇧🇿', '🇧🇿'), ('🇧🇯', '🇧🇯'), ('🇧🇲', '🇧🇲'), ('🇧🇹', '🇧🇹'), ('🇧🇴', '🇧🇴'), ('🇧🇦', '🇧🇦'),
              ('🇧🇼', '🇧🇼'), ('🇧🇻', '🇧🇻'), ('🇧🇷', '🇧🇷'), ('🇮🇴', '🇮🇴'), ('🇻🇬', '🇻🇬'), ('🇧🇳', '🇧🇳'), ('🇧🇬', '🇧🇬'),
              ('🇧🇫', '🇧🇫'), ('🇧🇮', '🇧🇮'), ('🇰🇭', '🇰🇭'), ('🇨🇲', '🇨🇲'), ('🇨🇦', '🇨🇦'), ('🇨🇻', '🇨🇻'), ('🇧🇶', '🇧🇶'),
              ('🇰🇾', '🇰🇾'), ('🇨🇫', '🇨🇫'), ('🇹🇩', '🇹🇩'), ('🇨🇱', '🇨🇱'), ('🇨🇳', '🇨🇳'), ('🇨🇽', '🇨🇽'), ('🇨🇨', '🇨🇨'),
              ('🇨🇴', '🇨🇴'), ('🇰🇲', '🇰🇲'), ('🇨🇬', '🇨🇬'), ('🇨🇩', '🇨🇩'), ('🇨🇰', '🇨🇰'), ('🇨🇷', '🇨🇷'), ('🇨🇮', '🇨🇮'),
              ('🇭🇷', '🇭🇷'), ('🇨🇺', '🇨🇺'), ('🇨🇼', '🇨🇼'), ('🇨🇾', '🇨🇾'), ('🇨🇿', '🇨🇿'), ('🇩🇰', '🇩🇰'), ('🇩🇯', '🇩🇯'),
              ('🇩🇲', '🇩🇲'), ('🇩🇴', '🇩🇴'), ('🇪🇨', '🇪🇨'), ('🇪🇬', '🇪🇬'), ('🇸🇻', '🇸🇻'), ('🇬🇶', '🇬🇶'), ('🇪🇷', '🇪🇷'),
              ('🇪🇪', '🇪🇪'), ('🇪🇹', '🇪🇹'), ('🇫🇰', '🇫🇰'), ('🇫🇴', '🇫🇴'), ('🇫🇯', '🇫🇯'), ('🇫🇮', '🇫🇮'), ('🇫🇷', '🇫🇷'),
              ('🇬🇫', '🇬🇫'), ('🇵🇫', '🇵🇫'), ('🇹🇫', '🇹🇫'), ('🇬🇦', '🇬🇦'), ('🇬🇲', '🇬🇲'), ('🇬🇪', '🇬🇪'), ('🇩🇪', '🇩🇪'),
              ('🇬🇭', '🇬🇭'), ('🇬🇮', '🇬🇮'), ('🇬🇷', '🇬🇷'), ('🇬🇱', '🇬🇱'), ('🇬🇩', '🇬🇩'), ('🇬🇵', '🇬🇵'), ('🇬🇺', '🇬🇺'),
              ('🇬🇹', '🇬🇹'), ('🇬🇼', '🇬🇼'), ('🇬🇾', '🇬🇾'), ('🇭🇹', '🇭🇹'), ('🇭🇲', '🇭🇲'), ('🇭🇳', '🇭🇳'), ('🇭🇰', '🇭🇰'),
              ('🇭🇺', '🇭🇺'), ('🇮🇸', '🇮🇸'), ('🇮🇳', '🇮🇳'), ('🇮🇩', '🇮🇩'), ('🇮🇷', '🇮🇷'), ('🇮🇶', '🇮🇶'), ('🇮🇪', '🇮🇪'),
              ('🇮🇱', '🇮🇱'), ('🇮🇹', '🇮🇹'), ('🇯🇲', '🇯🇲'), ('🇯🇵', '🇯🇵'), ('🇯🇪', '🇯🇪'), ('🇯🇴', '🇯🇴'), ('🇰🇿', '🇰🇿'),
              ('🇰🇪', '🇰🇪'), ('🇰🇮', '🇰🇮'), ('🇰🇵', '🇰🇵'), ('🇰🇷', '🇰🇷'), ('🇰🇼', '🇰🇼'), ('🇰🇬', '🇰🇬'), ('🇱🇦', '🇱🇦'),
              ('🇱🇻', '🇱🇻'), ('🇱🇧', '🇱🇧'), ('🇱🇸', '🇱🇸'), ('🇱🇷', '🇱🇷'), ('🇱🇾', '🇱🇾'), ('🇱🇮', '🇱🇮'), ('🇱🇹', '🇱🇹'),
              ('🇱🇺', '🇱🇺'), ('🇲🇴', '🇲🇴'), ('🇲🇰', '🇲🇰'), ('🇲🇬', '🇲🇬'), ('🇲🇼', '🇲🇼'), ('🇲🇾', '🇲🇾'), ('🇲🇻', '🇲🇻'),
              ('🇲🇱', '🇲🇱'), ('🇲🇹', '🇲🇹'), ('🇲🇭', '🇲🇭'), ('🇲🇶', '🇲🇶'), ('🇲🇷', '🇲🇷'), ('🇲🇺', '🇲🇺'), ('🇾🇹', '🇾🇹'),
              ('🇲🇽', '🇲🇽'), ('🇫🇲', '🇫🇲'), ('🇲🇩', '🇲🇩'), ('🇲🇨', '🇲🇨'), ('🇲🇳', '🇲🇳'), ('🇲🇪', '🇲🇪'), ('🇲🇸', '🇲🇸'),
              ('🇲🇦', '🇲🇦'), ('🇲🇿', '🇲🇿'), ('🇲🇲', '🇲🇲'), ('🇳🇦', '🇳🇦'), ('🇳🇷', '🇳🇷'), ('🇳🇵', '🇳🇵'), ('🇳🇱', '🇳🇱'),
              ('🇳🇨', '🇳🇨'), ('🇳🇿', '🇳🇿'), ('🇳🇮', '🇳🇮'), ('🇳🇪', '🇳🇪'), ('🇳🇬', '🇳🇬'), ('🇳🇺', '🇳🇺'), ('🇳🇫', '🇳🇫'),
              ('🇰🇵', '🇰🇵'), ('🇳🇴', '🇳🇴'), ('🇴🇲', '🇴🇲'), ('🇵🇰', '🇵🇰'), ('🇵🇼', '🇵🇼'), ('🇵🇸', '🇵🇸'), ('🇵🇦', '🇵🇦'),
              ('🇵🇬', '🇵🇬'), ('🇵🇾', '🇵🇾'), ('🇵🇪', '🇵🇪'), ('🇵🇭', '🇵🇭'), ('🇵🇳', '🇵🇳'), ('🇵🇱', '🇵🇱'), ('🇵🇹', '🇵🇹'),
              ('🇵🇷', '🇵🇷'), ('🇶🇦', '🇶🇦'), ('🇷🇪', '🇷🇪'), ('🇷🇴', '🇷🇴'), ('🇷🇺', '🇷🇺'), ('🇷🇼', '🇷🇼'), ('🇸🇭', '🇸🇭'),
              ('🇰🇳', '🇰🇳'), ('🇱🇨', '🇱🇨'), ('🇵🇲', '🇵🇲'), ('🇻🇨', '🇻🇨'), ('🇼🇸', '🇼🇸'), ('🇸🇲', '🇸🇲'), ('🇸🇹', '🇸🇹'),
              ('🇸🇦', '🇸🇦'), ('🇸🇳', '🇸🇳'), ('🇷🇸', '🇷🇸'), ('🇸🇨', '🇸🇨'), ('🇸🇱', '🇸🇱'), ('🇸🇬', '🇸🇬'), ('🇸🇰', '🇸🇰'),
              ('🇸🇮', '🇸🇮'), ('🇸🇧', '🇸🇧'), ('🇸🇴', '🇸🇴'), ('🇿🇦', '🇿🇦'), ('🇬🇸', '🇬🇸'), ('🇰🇷', '🇰🇷'), ('🇪🇸', '🇪🇸'),
              ('🇱🇰', '🇱🇰'), ('🇸🇩', '🇸🇩'), ('🇸🇷', '🇸🇷'), ('🇸🇿', '🇸🇿'), ('🇸🇪', '🇸🇪'), ('🇨🇭', '🇨🇭'), ('🇸🇾', '🇸🇾'),
              ('🇹🇼', '🇹🇼'), ('🇹🇯', '🇹🇯'), ('🇹🇿', '🇹🇿'), ('🇹🇭', '🇹🇭'), ('🇹🇱', '🇹🇱'), ('🇹🇬', '🇹🇬'), ('🇹🇰', '🇹🇰'),
              ('🇹🇴', '🇹🇴'), ('🇹🇹', '🇹🇹'), ('🇹🇳', '🇹🇳'), ('🇹🇷', '🇹🇷'), ('🇹🇲', '🇹🇲'), ('🇹🇨', '🇹🇨'), ('🇹🇻', '🇹🇻'),
              ('🇺🇬', '🇺🇬'), ('🇺🇦', '🇺🇦'), ('🇦🇪', '🇦🇪'), ('🇬🇧', '🇬🇧'), ('🇺🇸', '🇺🇸'), ('🇺🇾', '🇺🇾'), ('🇺🇿', '🇺🇿'),
              ('🇻🇺', '🇻🇺'), ('🇻🇦', '🇻🇦'), ('🇻🇪', '🇻🇪'), ('🇻🇳', '🇻🇳'), ('🇻🇬', '🇻🇬'), ('🇼🇫', '🇼🇫'), ('🇪🇭', '🇪🇭'),
              ('🇾🇪', '🇾🇪'), ('🇿🇲', '🇿🇲'), ('🇿🇼', '🇿🇼'),)

Calling_Code = (('93', '93'), ('355', '355'), ('213', '213'), ('1684', '1684'), ('376', '376'), ('244', '244'),
                ('1264', '1264'), ('672', '672'), ('1268', '1268'), ('54', '54'), ('374', '374'), ('297', '297'),
                ('61', '61'), ('43', '43'), ('994', '994'), ('1242', '1242'), ('973', '973'), ('880', '880'),
                ('1246', '1246'), ('375', '375'), ('32', '32'), ('501', '501'), ('229', '229'), ('1441', '1441'),
                ('975', '975'), ('591', '591'), ('387', '387'), ('267', '267'), ('47', '47'), ('55', '55'),
                ('246', '246'), ('673', '673'), ('359', '359'), ('226', '226'), ('257', '257'), ('855', '855'),
                ('237', '237'), ('1', '1'), ('238', '238'), ('1345', '1345'), ('236', '236'), ('235', '235'),
                ('56', '56'), ('86', '86'), ('61', '61'), ('61', '61'), ('57', '57'), ('269', '269'), ('242', '242'),
                ('243', '243'), ('682', '682'), ('506', '506'), ('225', '225'), ('385', '385'), ('53', '53'),
                ('357', '357'), ('420', '420'), ('45', '45'), ('253', '253'), ('1767', '1767'), ('1809', '1809'),
                ('593', '593'), ('20', '20'), ('503', '503'), ('240', '240'), ('291', '291'), ('372', '372'),
                ('251', '251'), ('500', '500'), ('298', '298'), ('679', '679'), ('358', '358'), ('33', '33'),
                ('594', '594'), ('689', '689'), ('262', '262'), ('241', '241'), ('220', '220'), ('995', '995'),
                ('49', '49'), ('233', '233'), ('350', '350'), ('30', '30'), ('299', '299'), ('1473', '1473'),
                ('590', '590'), ('1671', '1671'), ('502', '502'), ('224', '224'), ('245', '245'), ('592', '592'),
                ('509', '509'), ('504', '504'), ('852', '852'), ('36', '36'), ('354', '354'), ('91', '91'),
                ('62', '62'), ('98', '98'), ('964', '964'), ('353', '353'), ('972', '972'), ('39', '39'),
                ('1876', '1876'), ('81', '81'), ('44', '44'), ('962', '962'), ('7', '7'), ('254', '254'),
                ('686', '686'), ('850', '850'), ('82', '82'), ('965', '965'), ('996', '996'), ('856', '856'),
                ('371', '371'), ('961', '961'), ('266', '266'), ('231', '231'), ('218', '218'), ('423', '423'),
                ('370', '370'), ('352', '352'), ('853', '853'), ('389', '389'), ('261', '261'), ('265', '265'),
                ('60', '60'), ('960', '960'), ('223', '223'), ('356', '356'), ('692', '692'), ('596', '596'),
                ('222', '222'), ('230', '230'), ('269', '269'), ('52', '52'), ('691', '691'), ('373', '373'),
                ('377', '377'), ('976', '976'), ('1664', '1664'), ('212', '212'), ('258', '258'), ('95', '95'),
                ('264', '264'), ('674', '674'), ('977', '977'), ('31', '31'), ('599', '599'), ('687', '687'),
                ('64', '64'), ('505', '505'), ('227', '227'), ('234', '234'), ('683', '683'), ('672', '672'),
                ('1670', '1670'), ('47', '47'), ('968', '968'), ('92', '92'), ('680', '680'), ('970', '970'),
                ('507', '507'), ('675', '675'), ('595', '595'), ('51', '51'), ('63', '63'), ('64', '64'), ('48', '48'),
                ('351', '351'), ('1787', '1787'), ('974', '974'), ('262', '262'), ('40', '40'), ('7', '7'),
                ('250', '250'), ('290', '290'), ('1869', '1869'), ('1758', '1758'), ('508', '508'), ('1784', '1784'),
                ('684', '684'), ('378', '378'), ('239', '239'), ('966', '966'), ('221', '221'), ('381', '381'),
                ('248', '248'), ('232', '232'), ('65', '65'), ('421', '421'), ('386', '386'), ('677', '677'),
                ('252', '252'), ('27', '27'), ('500', '500'), ('34', '34'), ('94', '94'), ('249', '249'),
                ('597', '597'), ('47', '47'), ('268', '268'), ('46', '46'), ('41', '41'), ('963', '963'),
                ('886', '886'), ('992', '992'), ('255', '255'), ('66', '66'), ('670', '670'), ('228', '228'),
                ('690', '690'), ('676', '676'), ('1868', '1868'), ('216', '216'), ('993', '993'), ('688', '688'),
                ('256', '256'), ('380', '380'), ('44', '44'), ('1', '1'), ('598', '598'), ('998', '998'),
                ('678', '678'), ('58', '58'), ('84', '84'), ('1284', '1284'), ('1340', '1340'), ('681', '681'),
                ('212', '212'), ('967', '967'), ('260', '260'), ('263', '263'),)
#################### Egypt Cities ####################

############### Governorates List ###############
Governorates_List = (('Alexandria', _('Alexandria')), ('Aswan', _('Aswan')), ('Asyut', _('Asyut')),
                     ('Beheira', _('Beheira')), ('Beni Suef', _('Beni Suef')), ('Cairo', _('Cairo')),
                     ('Dakahlia', _('Dakahlia')), ('Damietta', _('Damietta')), ('Faiyum', _('Faiyum')),
                     ('Gharbia', _('Gharbia')), ('Giza', _('Giza')), ('Ismailia', _('Ismailia')),
                     ('Kafr El Sheikh', _('Kafr El Sheikh')), ('Luxor', _('Luxor')), ('Matruh', _('Matruh')),
                     ('Minya', _('Minya')), ('Monufia', _('Monufia')), ('New Valley', _('New Valley')),
                     ('North Sinai', _('North Sinai')), ('Port Said', _('Port Said')), ('Qalyubia', _('Qalyubia')),
                     ('Qena', _('Qena')), ('Red Sea', _('Red Sea')), ('Sharqia', _('Sharqia')), ('Sohag', _('Sohag')),
                     ('South Sinai', _('South Sinai')), ('Suez', _('Suez')),)
SAUDI_CITIES_BY_GOVERNORATE = (
    ('Riyadh', _('Riyadh')),
    ('Jeddah', _('Jeddah')),
    ('Mecca', _('Mecca')),
    ('Medina', _('Medina')),
    ('Dammam', _('Dammam')),
    ('Khobar', _('Khobar')),
    ('Dhahran', _('Dhahran')),
    ('Tabuk', _('Tabuk')),
    ('Abha', _('Abha')),
    ('Khamis Mushait', _('Khamis Mushait')),
    ('Buraidah', _('Buraidah')),
    ('Hail', _('Hail')),
    ('Najran', _('Najran')),
    ('Jazan', _('Jazan')),
)
############### City List ###############


############### Language List ###############
Language_List = (('Arabic', _('Arabic')), ('English', _('English')), ('French', _('French')), ('German', _('German')),
                 ('Italian', _('Italian')), ('Japanese', _('Japanese')), ('Korean', _('Korean')),
                 ('Portuguese', _('Portuguese')), ('Russian', _('Russian')), ('Spanish', _('Spanish')),
                 ('Turkish', _('Turkish')), ('Chinese', _('Chinese')),)
############### Currency List ###############
Currency_List = (('USD', _('USD')), ('EUR', _('EUR')), ('GBP', _('GBP')), ('JPY', _('JPY')), ('AUD', _('AUD')),
                 ('CAD', _('CAD')), ('CHF', _('CHF')), ('CNY', _('CNY')), ('SEK', _('SEK')), ('NZD', _('NZD')),
                 ('MXN', _('MXN')), ('SGD', _('SGD')), ('HKD', _('HKD')), ('NOK', _('NOK')), ('KRW', _('KRW')),
                 ('TRY', _('TRY')), ('RUB', _('RUB')), ('INR', _('INR')), ('BRL', _('BRL')), ('ZAR', _('ZAR')),
                 ('DKK', _('DKK')), ('PLN', _('PLN')), ('TWD', _('TWD')), ('THB', _('THB')), ('IDR', _('IDR')),
                 ('HUF', _('HUF')), ('CZK', _('CZK')), ('ILS', _('ILS')), ('CLP', _('CLP')), ('PHP', _('PHP')),
                 ('AED', _('AED')), ('COP', _('COP')), ('SAR', _('SAR')), ('MYR', _('MYR')), ('RON', _('RON')),
                 ('ARS', _('ARS')), ('PEN', _('PEN')), ('PKR', _('PKR')), ('IQD', _('IQD')), ('QAR', _('QAR')),
                 ('KWD', _('KWD')), ('OMR', _('OMR')), ('BHD', _('BHD')), ('JOD', _('JOD')), ('LBP', _('LBP')),
                 ('EGP', _('EGP')), ('BDT', _('BDT')), ('NGN', _('NGN')), ('TZS', _('TZS')), ('UGX', _('UGX')),
                 ('GHS', _('GHS')), ('KES', _('KES')), ('XAF', _('XAF')), ('XOF', _('XOF')), ('XPF', _('XPF')),
                 ('MAD', _('MAD')), ('DZD', _('DZD')), ('TND', _('TND')), ('MRO', _('MRO')), ('LYD', _('LYD')),
                 ('TMT', _('TMT')), ('MZN', _('MZN')), ('GMD', _('GMD')), ('AOA', _('AOA')), ('ZMW', _('ZMW')),
                 ('CDF', _('CDF')), ('BIF', _('BIF')), ('RWF', _('RWF')), ('STD', _('STD')), ('SLL', _('SLL')),
                 ('LRD', _('LRD')), ('GEL', _('GEL')), ('AMD', _('AMD')), ('ALL', _('ALL')), ('HNL', _('HNL')),
                 ('NIO', _('NIO')), ('CRC', _('CRC')), ('MKD', _('MKD')), ('BAM', _('BAM')), ('TOP', _('TOP')),
                 ('FJD', _('FJD')), ('BBD', _('BBD')), ('BSD', _('BSD')), ('BZD', _('BZD')), ('BMD', _('BMD')),
                 ('SBD', _('SBD')), ('SRD', _('SRD')), ('GYD', _('GYD')), ('AZN', _('AZN')), ('SVC', _('SVC')),
                 ('PGK', _('PGK')), ('LAK', _('LAK')), ('SOS', _('SOS')), ('MMK', _('MMK')), ('KGS', _('KGS')),
                 ('UZS', _('UZS')), ('TJS', _('TJS')), ('MOP', _('MOP')), ('KZT', _('KZT')), ('KPW', _('KPW')),
                 ('SSP', _('SSP')), ('SYP', _('SYP')), ('YER', _('YER')), ('TWD', _('TWD')), ('MRU', _('MRU')),
                 ('BYN', _('BYN')), ('BGN', _('BGN')), ('CDF', _('CDF')), ('BAM', _('BAM')), ('BBD', _('BBD')),
                 ('BMD', _('BMD')), ('BND', _('BND')), ('BSD', _('BSD')), ('BWP', _('BWP')), ('BZD', _('BZD')),
                 ('CAD', _('CAD')), ('CLP', _('CLP')), ('CNY', _('CNY')), ('COP', _('COP')), ('CRC', _('CRC')),
                 ('CUP', _('CUP')), ('CZK', _('CZK')), ('DKK', _('DKK')), ('DOP', _('DOP')), ('EGP', _('EGP')),
                 ('EUR', _('EUR')), ('FJD', _('FJD')), ('GBP', _('GBP')), ('GHS', _('GHS')), ('GMD', _('GMD')),
                 ('GTQ', _('GTQ')), ('GYD', _('GYD')), ('HKD', _('HKD')), ('HRK', _('HRK')), ('HUF', _('HUF')),
                 ('IDR', _('IDR')), ('ILS', _('ILS')), ('INR', _('INR')), ('ISK', _('ISK')), ('JMD', _('JMD')),
                 ('JPY', _('JPY')), ('KES', _('KES')), ('KGS', _('KGS')), ('KHR', _('KHR')), ('KRW', _('KRW')),
                 ('KYD', _('KYD')), ('KZT', _('KZT')), ('LAK', _('LAK')), ('LBP', _('LBP')), ('LKR', _('LKR')),
                 ('LRD', _('LRD')), ('MAD', _('MAD')), ('MDL', _('MDL')), ('MKD', _('MKD')), ('MMK', _('MMK')),
                 ('MNT', _('MNT')), ('MOP', _('MOP')), ('MUR', _('MUR')), ('MVR', _('MVR')), ('MWK', _('MWK')),
                 ('MXN', _('MXN')), ('MYR', _('MYR')), ('MZN', _('MZN')), ('NAD', _('NAD')), ('NGN', _('NGN')),
                 ('NIO', _('NIO')), ('NOK', _('NOK')), ('NPR', _('NPR')), ('NZD', _('NZD')), ('PAB', _('PAB')),
                 ('PEN', _('PEN')), ('PGK', _('PGK')), ('PHP', _('PHP')), ('PKR', _('PKR')), ('PLN', _('PLN')),
                 ('PYG', _('PYG')), ('QAR', _('QAR')), ('RON', _('RON')), ('RSD', _('RSD')), ('RUB', _('RUB')),
                 ('RWF', _('RWF')), ('SAR', _('SAR')), ('SBD', _('SBD')), ('SCR', _('SCR')), ('SEK', _('SEK')),
                 ('SGD', _('SGD')), ('SLL', _('SLL')), ('SOS', _('SOS')), ('SRD', _('SRD')), ('STD', _('STD')),
                 ('SVC', _('SVC')), ('SZL', _('SZL')), ('THB', _('THB')), ('TJS', _('TJS')), ('TOP', _('TOP')),
                 ('TRY', _('TRY')), ('TTD', _('TTD')), ('TWD', _('TWD')),

                 ('TZS', _('TZS')), ('UAH', _('UAH')), ('UGX', _('UGX')), ('USD', _('USD')), ('UYU', _('UYU')),
                 ('UZS', _('UZS')), ('VEF', _('VEF')), ('VND', _('VND')), ('VUV', _('VUV')), ('WST', _('WST')),
                 ('XAF', _('XAF')), ('XCD', _('XCD')), ('XOF', _('XOF')), ('XPF', _('XPF')), ('YER', _('YER')),
                 ('ZAR', _('ZAR')), ('ZMW', _('ZMW')), ('ZWL', _('ZWL')),)
currency_position = (('left', _('left')), ('right', _('right')),)
############### Timezone List ###############
Timezone_List = (('Africa/Abidjan', _('Africa/Abidjan')), ('Africa/Accra', _('Africa/Accra')),
                 ('Africa/Addis_Ababa', _('Africa/Addis_Ababa')), ('Africa/Algiers', _('Africa/Algiers')),
                 ('Africa/Asmara', _('Africa/Asmara')), ('Africa/Asmera', _('Africa/Asmera')),
                 ('Africa/Bamako', _('Africa/Bamako')), ('Africa/Bangui', _('Africa/Bangui')),
                 ('Africa/Banjul', _('Africa/Banjul')), ('Africa/Bissau', _('Africa/Bissau')),
                 ('Africa/Blantyre', _('Africa/Blantyre')), ('Africa/Brazzaville', _('Africa/Brazzaville')),
                 ('Africa/Bujumbura', _('Africa/Bujumbura')), ('Africa/Cairo', _('Africa/Cairo')),
                 ('Africa/Casablanca', _('Africa/Casablanca')), ('Africa/Ceuta', _('Africa/Ceuta')),
                 ('Africa/Conakry', _('Africa/Conakry')), ('Africa/Dakar', _('Africa/Dakar')),
                 ('Africa/Dar_es_Salaam', _('Africa/Dar_es_Salaam')), ('Africa/Djibouti', _('Africa/Djibouti')),
                 ('Africa/Douala', _('Africa/Douala')), ('Africa/El_Aaiun', _('Africa/El_Aaiun')),
                 ('Africa/Freetown', _('Africa/Freetown')), ('Africa/Gaborone', _('Africa/Gaborone')),
                 ('Africa/Harare', _('Africa/Harare')), ('Africa/Johannesburg', _('Africa/Johannesburg')),
                 ('Africa/Juba', _('Africa/Juba')), ('Africa/Kampala', _('Africa/Kampala')),
                 ('Africa/Khartoum', _('Africa/Khartoum')), ('Africa/Kigali', _('Africa/Kigali')),
                 ('Africa/Kinshasa', _('Africa/Kinshasa')), ('Africa/Lagos', _('Africa/Lagos')),
                 ('Africa/Libreville', _('Africa/Libreville')), ('Africa/Lome', _('Africa/Lome')),
                 ('Africa/Luanda', _('Africa/Luanda')), ('Africa/Lubumbashi', _('Africa/Lubumbashi')),
                 ('Africa/Lusaka', _('Africa/Lusaka')), ('Africa/Malabo', _('Africa/Malabo')),
                 ('Africa/Maputo', _('Africa/Maputo')), ('Africa/Maseru', _('Africa/Maseru')),
                 ('Africa/Mbabane', _('Africa/Mbabane')), ('Africa/Mogadishu', _('Africa/Mogadishu')),
                 ('Africa/Monrovia', _('Africa/Monrovia')), ('Africa/Nairobi', _('Africa/Nairobi')),
                 ('Africa/Ndjamena', _('Africa/Ndjamena')), ('Africa/Niamey', _('Africa/Niamey')),
                 ('Africa/Nouakchott', _('Africa/Nouakchott')), ('Africa/Ouagadougou', _('Africa/Ouagadougou')),
                 ('Africa/Porto-Novo', _('Africa/Porto-Novo')), ('Africa/Sao_Tome', _('Africa/Sao_Tome')),
                 ('Africa/Timbuktu', _('Africa/Timbuktu')), ('Africa/Tripoli', _('Africa/Tripoli')),
                 ('Africa/Tunis', _('Africa/Tunis')), ('Africa/Windhoek', _('Africa/Windhoek')),
                 ('America/Adak', _('America/Adak')), ('America/Anchorage', _('America/Anchorage')),
                 ('America/Anguilla', _('America/Anguilla')), ('America/Antigua', _('America/Antigua')),
                 ('America/Araguaina', _('America/Araguaina')),
                 ('America/Argentina/Buenos_Aires', _('America/Argentina/Buenos_Aires')),
                 ('America/Argentina/Catamarca', _('America/Argentina/Catamarca')),
                 ('America/Argentina/ComodRivadavia', _('America/Argentina/ComodRivadavia')),
                 ('America/Argentina/Cordoba', _('America/Argentina/Cordoba')),
                 ('America/Argentina/Jujuy', _('America/Argentina/Jujuy')),
                 ('America/Argentina/La_Rioja', _('America/Argentina/La_Rioja')),
                 ('America/Argentina/Mendoza', _('America/Argentina/Mendoza')),
                 ('America/Argentina/Rio_Gallegos', _('America/Argentina/Rio_Gallegos')),
                 ('America/Argentina/Salta', _('America/Argentina/Salta')),
                 ('America/Argentina/San_Juan', _('America/Argentina/San_Juan')),
                 ('America/Argentina/San_Luis', _('America/Argentina/San_Luis')),
                 ('America/Argentina/Tucuman', _('America/Argentina/Tucuman')),
                 ('America/Argentina/Ushuaia', _('America/Argentina/Ushuaia')), ('America/Aruba', _('America/Aruba')),
                 ('America/Asuncion', _('America/Asuncion')), ('America/Atikokan', _('America/Atikokan')),
                 ('America/Atka', _('America/Atka')), ('America/Bahia', _('America/Bahia')),
                 ('America/Bahia_Banderas', _('America/Bahia_Banderas')), ('America/Barbados', _('America/Barbados')),
                 ('America/Belem', _('America/Belem')), ('America/Belize', _('America/Belize')),
                 ('America/Blanc-Sablon', _('America/Blanc-Sablon')), ('America/Boa_Vista', _('America/Boa_Vista')),
                 ('America/Bogota', _('America/Bogota')), ('America/Boise', _('America/Boise')),
                 ('America/Buenos_Aires', _('America/Buenos_Aires')),
                 ('America/Cambridge_Bay', _('America/Cambridge_Bay')),
                 ('America/Campo_Grande', _('America/Campo_Grande')), ('America/Cancun', _('America/Cancun')),
                 ('America/Caracas', _('America/Caracas')), ('America/Catamarca', _('America/Catamarca')),
                 ('America/Cayenne', _('America/Cayenne')), ('America/Cayman', _('America/Cayman')),
                 ('America/Chicago', _('America/Chicago')), ('America/Chihuahua', _('America/Chihuahua')),
                 ('America/Coral_Harbour', _('America/Coral_Harbour')),

                 ('America/Cordoba', _('America/Cordoba')), ('America/Costa_Rica', _('America/Costa_Rica')),
                 ('America/Creston', _('America/Creston')), ('America/Cuiaba', _('America/Cuiaba')),
                 ('America/Curacao', _('America/Curacao')), ('America/Danmarkshavn', _('America/Danmarkshavn')),
                 ('America/Dawson', _('America/Dawson')), ('America/Dawson_Creek', _('America/Dawson_Creek')),
                 ('America/Denver', _('America/Denver')), ('America/Detroit', _('America/Detroit')),
                 ('America/Dominica', _('America/Dominica')), ('America/Edmonton', _('America/Edmonton')),
                 ('America/Eirunepe', _('America/Eirunepe')), ('America/El_Salvador', _('America/El_Salvador')),
                 ('America/Ensenada', _('America/Ensenada')), ('America/Fort_Wayne', _('America/Fort_Wayne')),
                 ('America/Fortaleza', _('America/Fortaleza')), ('America/Glace_Bay', _('America/Glace_Bay')),
                 ('America/Godthab', _('America/Godthab')), ('America/Goose_Bay', _('America/Goose_Bay')),
                 ('America/Grand_Turk', _('America/Grand_Turk')), ('America/Grenada', _('America/Grenada')),
                 ('America/Guadeloupe', _('America/Guadeloupe')), ('America/Guatemala', _('America/Guatemala')),
                 ('America/Guayaquil', _('America/Guayaquil')), ('America/Guyana', _('America/Guyana')),
                 ('America/Halifax', _('America/Halifax')), ('America/Havana', _('America/Havana')),
                 ('America/Hermosillo', _('America/Hermosillo')),
                 ('America/Indiana/Indianapolis', _('America/Indiana/Indianapolis')),
                 ('America/Indiana/Knox', _('America/Indiana/Knox')),
                 ('America/Indiana/Marengo', _('America/Indiana/Marengo')),
                 ('America/Indiana/Petersburg', _('America/Indiana/Petersburg')),
                 ('America/Indiana/Tell_City', _('America/Indiana/Tell_City')),
                 ('America/Indiana/Vevay', _('America/Indiana/Vevay')),
                 ('America/Indiana/Vincennes', _('America/Indiana/Vincennes')),
                 ('America/Indiana/Winamac', _('America/Indiana/Winamac')),
                 ('America/Indianapolis', _('America/Indianapolis')), ('America/Inuvik', _('America/Inuvik')),
                 ('America/Iqaluit', _('America/Iqaluit')), ('America/Jamaica', _('America/Jamaica')),
                 ('America/Jujuy', _('America/Jujuy')), ('America/Juneau', _('America/Juneau')),
                 ('America/Kentucky/Louisville', _('America/Kentucky/Louisville')),
                 ('America/Kentucky/Monticello', _('America/Kentucky/Monticello')),
                 ('America/Knox_IN', _('America/Knox_IN')), ('America/Kralendijk', _('America/Kralendijk')),
                 ('America/La_Paz', _('America/La_Paz')), ('America/Lima', _('America/Lima')),
                 ('America/Los_Angeles', _('America/Los_Angeles')), ('America/Louisville', _('America/Louisville')),
                 ('America/Lower_Princes', _('America/Lower_Princes')), ('America/Maceio', _('America/Maceio')),
                 ('America/Managua', _('America/Managua')), ('America/Manaus', _('America/Manaus')),
                 ('America/Marigot', _('America/Marigot')), ('America/Martinique', _('America/Martinique')),
                 ('America/Matamoros', _('America/Matamoros')), ('America/Mazatlan', _('America/Mazatlan')),
                 ('America/Mendoza', _('America/Mendoza')), ('America/Menominee', _('America/Menominee')),
                 ('America/Merida', _('America/Merida')), ('America/Metlakatla', _('America/Metlakatla')),
                 ('America/Mexico_City', _('America/Mexico_City')), ('America/Miquelon', _('America/Miquelon')),
                 ('America/Moncton', _('America/Moncton')), ('America/Monterrey', _('America/Monterrey')),
                 ('America/Montevideo', _('America/Montevideo')), ('America/Montreal', _('America/Montreal')),
                 ('America/Montserrat', _('America/Montserrat')), ('America/Nassau', _('America/Nassau')),
                 ('America/New_York', _('America/New_York')), ('America/Nipigon', _('America/Nipigon')),
                 ('America/Nome', _('America/Nome')), ('America/Noronha', _('America/Noronha')),
                 ('America/North_Dakota/Beulah', _('America/North_Dakota/Beulah')),
                 ('America/North_Dakota/Center', _('America/North_Dakota/Center')),
                 ('America/North_Dakota/New_Salem', _('America/North_Dakota/New_Salem')),
                 ('America/Ojinaga', _('America/Ojinaga')), ('America/Panama', _('America/Panama')),
                 ('America/Pangnirtung', _('America/Pangnirtung')), ('America/Paramaribo', _('America/Paramaribo')),
                 ('America/Phoenix', _('America/Phoenix')), ('America/Port-au-Prince', _('America/Port-au-Prince')),
                 ('America/Port_of_Spain', _('America/Port_of_Spain')), ('America/Porto_Acre', _('America/Porto_Acre')),
                 ('America/Porto_Velho', _('America/Porto_Velho')), ('America/Puerto_Rico', _('America/Puerto_Rico')),
                 ('America/Rainy_River', _('America/Rainy_River')), ('America/Rankin_Inlet', _('America/Rankin_Inlet')),
                 ('America/Recife', _('America/Recife')), ('America/Regina', _('America/Regina')),
                 ('America/Resolute', _('America/Resolute')), ('America/Rio_Branco', _('America/Rio_Branco')),
                 ('America/Rosario', _('America/Rosario')), ('America/Santa_Isabel', _('America/Santa_Isabel')),
                 ('America/Santarem', _('America/Santarem')), ('America/Santiago', _('America/Santiago')),
                 ('America/Santo_Domingo', _('America/Santo_Domingo')), ('America/Sao_Paulo', _('America/Sao_Paulo')),
                 ('America/Scoresbysund', _('America/Scoresbysund')), ('America/Shiprock', _('America/Shiprock')),
                 ('America/Sitka', _('America/Sitka')), ('America/St_Barthelemy', _('America/St_Barthelemy')),
                 ('America/St_Johns', _('America/St_Johns')), ('America/St_Kitts', _('America/St_Kitts')),
                 ('America/St_Lucia', _('America/St_Lucia')), ('America/St_Thomas', _('America/St_Thomas')),
                 ('America/St_Vincent', _('America/St_Vincent')), ('America/Swift_Current', _('America/Swift_Current')),
                 ('America/Tegucigalpa', _('America/Tegucigalpa')), ('America/Thule', _('America/Thule')),
                 ('America/Thunder_Bay', _('America/Thunder_Bay')), ('America/Tijuana', _('America/Tijuana')),
                 ('America/Toronto', _('America/Toronto')), ('America/Tortola', _('America/Tortola')),
                 ('America/Vancouver', _('America/Vancouver')), ('America/Virgin', _('America/Virgin')),
                 ('America/Whitehorse', _('America/Whitehorse')), ('America/Winnipeg', _('America/Winnipeg')),
                 ('America/Yakutat', _('America/Yakutat')), ('America/Yellowknife', _('America/Yellowknife')),
                 ('Antarctica/Casey', _('Antarctica/Casey')), ('Antarctica/Davis', _('Antarctica/Davis')),
                 ('Antarctica/DumontDUrville', _('Antarctica/DumontDUrville')),
                 ('Antarctica/Macquarie', _('Antarctica/Macquarie')), ('Antarctica/Mawson', _('Antarctica/Mawson')),
                 ('Antarctica/McMurdo', _('Antarctica/McMurdo')), ('Antarctica/Palmer', _('Antarctica/Palmer')),
                 ('Antarctica/Rothera', _('Antarctica/Rothera')), ('Antarctica/South_Pole', _('Antarctica/South_Pole')),
                 ('Antarctica/Syowa', _('Antarctica/Syowa')), ('Antarctica/Troll', _('Antarctica/Troll')),
                 ('Antarctica/Vostok', _('Antarctica/Vostok')), ('Arctic/Longyearbyen', _('Arctic/Longyearbyen')),
                 ('Asia/Aden', _('Asia/Aden')), ('Asia/Almaty', _('Asia/Almaty')), ('Asia/Amman', _('Asia/Amman')),
                 ('Asia/Anadyr', _('Asia/Anadyr')), ('Asia/Aqtau', _('Asia/Aqtau')), ('Asia/Aqtobe', _('Asia/Aqtobe')),
                 ('Asia/Ashgabat', _('Asia/Ashgabat')), ('Asia/Ashkhabad', _('Asia/Ashkhabad')),
                 ('Asia/Baghdad', _('Asia/Baghdad')), ('Asia/Bahrain', _('Asia/Bahrain')),
                 ('Asia/Baku', _('Asia/Baku')), ('Asia/Bangkok', _('Asia/Bangkok')), ('Asia/Beirut', _('Asia/Beirut')),
                 ('Asia/Bishkek', _('Asia/Bishkek')), ('Asia/Brunei', _('Asia/Brunei')),
                 ('Asia/Calcutta', _('Asia/Calcutta')), ('Asia/Choibalsan', _('Asia/Choibalsan')),
                 ('Asia/Chongqing', _('Asia/Chongqing')), ('Asia/Chungking', _('Asia/Chungking')),
                 ('Asia/Colombo', _('Asia/Colombo')), ('Asia/Dacca', _('Asia/Dacca')),
                 ('Asia/Damascus', _('Asia/Damascus')), ('Asia/Dhaka', _('Asia/Dhaka')), ('Asia/Dili', _('Asia/Dili')),
                 ('Asia/Dubai', _('Asia/Dubai')), ('Asia/Dushanbe', _('Asia/Dushanbe')),)
############### Color List ###############
COLORS = (('#F0F8FF', 'AliceBlue'), ('#FAEBD7', 'AntiqueWhite'), ('#00FFFF', 'Aqua'), ('#7FFFD4', 'Aquamarine'),
          ('#F0FFFF', 'Azure'), ('#F5F5DC', 'Beige'), ('#FFE4C4', 'Bisque'), ('#000000', 'Black'),
          ('#FFEBCD', 'BlanchedAlmond'), ('#0000FF', 'Blue'), ('#8A2BE2', 'BlueViolet'), ('#A52A2A', 'Brown'),
          ('#DEB887', 'BurlyWood'), ('#5F9EA0', 'CadetBlue'), ('#7FFF00', 'Chartreuse'), ('#D2691E', 'Chocolate'),
          ('#FF7F50', 'Coral'), ('#6495ED', 'CornflowerBlue'), ('#FFF8DC', 'Cornsilk'), ('#DC143C', 'Crimson'),
          ('#00FFFF', 'Cyan'), ('#00008B', 'DarkBlue'), ('#008B8B', 'DarkCyan'), ('#B8860B', 'DarkGoldenRod'),
          ('#A9A9A9', 'DarkGray'), ('#006400', 'DarkGreen'), ('#A9A9A9', 'DarkGrey'), ('#BDB76B', 'DarkKhaki'),
          ('#8B008B', 'DarkMagenta'), ('#556B2F', 'DarkOliveGreen'), ('#FF8C00', 'DarkOrange'),
          ('#9932CC', 'DarkOrchid'), ('#8B0000', 'DarkRed'), ('#E9967A', 'DarkSalmon'), ('#8FBC8F', 'DarkSeaGreen'),
          ('#483D8B', 'DarkSlateBlue'), ('#2F4F4F', 'DarkSlateGray'), ('#2F4F4F', 'DarkSlateGrey'),
          ('#00CED1', 'DarkTurquoise'), ('#9400D3', 'DarkViolet'), ('#FF1493', 'DeepPink'), ('#00BFFF', 'DeepSkyBlue'),
          ('#696969', 'DimGray'), ('#696969', 'DimGrey'), ('#1E90FF', 'DodgerBlue'), ('#B22222', 'FireBrick'),
          ('#FFFAF0', 'FloralWhite'), ('#228B22', 'ForestGreen'), ('#FF00FF', 'Fuchsia'), ('#DCDCDC', 'Gainsboro'),
          ('#F8F8FF', 'GhostWhite'), ('#FFD700', 'Gold'), ('#DAA520', 'GoldenRod'), ('#808080', 'Gray'),
          ('#008000', 'Green'), ('#ADFF2F', 'GreenYellow'), ('#808080', 'Grey'), ('#F0FFF0', 'HoneyDew'),
          ('#FF69B4', 'HotPink'), ('#CD5C5C', 'IndianRed'), ('#4B0082', 'Indigo'), ('#FFFFF0', 'Ivory'),
          ('#F0E68C', 'Khaki'), ('#E6E6FA', 'Lavender'), ('#FFF0F5', 'LavenderBlush'), ('#7CFC00', 'LawnGreen'),
          ('#FFFACD', 'LemonChiffon'), ('#ADD8E6', 'LightBlue'), ('#F08080', 'LightCoral'), ('#E0FFFF', 'LightCyan'),
          ('#FAFAD2', 'LightGoldenRodYellow'), ('#D3D3D3', 'LightGray'), ('#90EE90', 'LightGreen'),
          ('#D3D3D3', 'LightGrey'), ('#FFB6C1', 'LightPink'), ('#FFA07A', 'LightSalmon'), ('#20B2AA', 'LightSeaGreen'),
          ('#87CEFA', 'LightSkyBlue'), ('#778899', 'LightSlateGray'), ('#778899', 'LightSlateGrey'),
          ('#B0C4DE', 'LightSteelBlue'), ('#FFFFE0', 'LightYellow'), ('#00FF00', 'Lime'), ('#32CD32', 'LimeGreen'),
          ('#FAF0E6', 'Linen'), ('#FF00FF', 'Magenta'), ('#800000', 'Maroon'), ('#66CDAA', 'MediumAquaMarine'),
          ('#0000CD', 'MediumBlue'), ('#BA55D3', 'MediumOrchid'), ('#9370DB', 'MediumPurple'),
          ('#3CB371', 'MediumSeaGreen'), ('#7B68EE', 'MediumSlateBlue'), ('#00FA9A', 'MediumSpringGreen'),
          ('#48D1CC', 'MediumTurquoise'), ('#C71585', 'MediumVioletRed'), ('#191970', 'MidnightBlue'),
          ('#F5FFFA', 'MintCream'), ('#FFE4E1', 'MistyRose'), ('#FFE4B5', 'Moccasin'), ('#FFDEAD', 'NavajoWhite'),
          ('#000080', 'Navy'), ('#FDF5E6', 'OldLace'), ('#808000', 'Olive'), ('#6B8E23', 'OliveDrab'),
          ('#FFA500', 'Orange'), ('#FF4500', 'OrangeRed'), ('#DA70D6', 'Orchid'), ('#EEE8AA', 'PaleGoldenRod'),
          ('#98FB98', 'PaleGreen'), ('#AFEEEE', 'PaleTurquoise'), ('#DB7093', 'PaleVioletRed'),
          ('#FFEFD5', 'PapayaWhip'), ('#FFDAB9', 'PeachPuff'), ('#CD853F', 'Peru'), ('#FFC0CB', 'Pink'),
          ('#DDA0DD', 'Plum'), ('#B0E0E6', 'PowderBlue'), ('#800080', 'Purple'), ('#663399', 'RebeccaPurple'),
          ('#FF0000', 'Red'), ('#BC8F8F', 'RosyBrown'), ('#4169E1', 'RoyalBlue'), ('#8B4513', 'SaddleBrown'),
          ('#FA8072', 'Salmon'), ('#F4A460', 'SandyBrown'), ('#2E8B57', 'SeaGreen'), ('#FFF5EE', 'SeaShell'),
          ('#A0522D', 'Sienna'), ('#C0C0C0', 'Silver'), ('#87CEEB', 'SkyBlue'), ('#6A5ACD', 'SlateBlue'),
          ('#708090', 'SlateGray'), ('#708090', 'SlateGrey'), ('#FFFAFA', 'Snow'), ('#00FF7F', 'SpringGreen'),
          ('#4682B4', 'SteelBlue'), ('#D2B48C', 'Tan'), ('#008080', 'Teal'), ('#D8BFD8', 'Thistle'),
          ('#FF6347', 'Tomato'), ('#40E0D0', 'Turquoise'), ('#EE82EE', 'Violet'), ('#F5DEB3', 'Wheat'),
          ('#FFFFFF', 'White'), ('#F5F5F5', 'WhiteSmoke'), ('#FFFF00', 'Yellow'), ('#9ACD32', 'YellowGreen'),

)
############### Help Categories Helper ###############

Help_Categories = (("FAQ", _("FAQ")), ("Tutorials", _("Tutorials")), ('Videos', _('Videos')),
                   ('Documentations', _('Documentations')), ('Products ', _('Products ')),
                   ('Services ', _('Services ')), ('Other', _('Other')),)
############### Front Helper ###############
Page_Name = (('Home', 'Home'), ('About', 'About'), ('Contact', 'Contact'), ('Blog', 'Blog'), ('Other', 'Other'),)

Page_Type = (('Page', 'Page'), ('Post', 'Post'), ('Portfolio', 'Portfolio'), ('Product', 'Product'),
             ('Category', 'Category'), ('Brand', 'Brand'), ('Blog', 'Blog'), ('Other', 'Other'),)

Block_Type = (('Slider', 'Slider'), ('Banner', 'Banner'), ('Category', 'Category'), ('Product', 'Product'),
              ('Service', 'Service'), ('Clients', 'Clients'), ('Page', 'Page'), ('Portfolio', 'Portfolio'),
              ('Brand', 'Brand'), ('Blog', 'Blog'), ('HTML', 'HTML'), ('Text', 'Text'), ('Image', 'Image'),
              ('Video', 'Video'), ('Link', 'Link'), ('Contact', 'Contact'), ('Social', 'Social'),
              ('Subscribe', 'Subscribe'), ('Testimonial', 'Testimonial'), ('Map', 'Map'), ('Menu', 'Menu'),
              ('Footer', 'Footer'), ('Header', 'Header'), ('Portfolio', 'Portfolio'), ('Other', 'Other'),)
Block_Item_Type = (('Info', 'Info'), ('Images', 'Images'), ('Video', 'Video'), ('Link', 'Link'), ('Other', 'Other'),)

Slider_Type = (('Default', 'Default'), ('Main', 'Main'), ('OurWork', 'OurWork'), ('Testimonial', 'Testimonial'),
               ('Other', 'Other'),)

Page_Style = (('Style 1', 'Style 1'), ('Style 2', 'Style 2'), ('Style 3', 'Style 3'),)
Page_Layout = (('Default', 'Default'), ('Left', 'Left'), ('Right', 'Right'), ('Other', 'Other'),)
Page_Sidebar = (('Default', 'Default'), ('Left', 'Left'), ('Right', 'Right'), ('Other', 'Other'),)
Page_Sidebar_Style = (('Default', 'Default'), ('Full', 'Full'), ('Boxed', 'Boxed'), ('Other', 'Other'),)
Page_Sidebar_Layout = (('Default', 'Default'), ('Left', 'Left'), ('Right', 'Right'), ('Other', 'Other'),)
Front_Category = (('Branding', 'Branding '), ('Social Media', 'Social Media'), ('Motion Graphic', 'Motion Graphic'),
                  ('Video Editing ', 'Video Editing'), ('Advertising', 'Advertising'), ('Printing ', 'Printing'),
                  ('Ui Design', 'Ui Design'), ('Other', 'Other'),)

############### Catalog Helper ###############
Coupon_Type = (('Default', 'Default'), ('Paid', 'Paid'), ('Free', 'Free'), ('Admin', 'Admin'),)
Discount_Type = (('Percentage', _('Percentage')), ('Fixed', _('Fixed')), (None, _('None')))
Availability = ((True, 'In stock'), (False, 'Out of stock'),)
Size = ((1, 'XS'), (2, 'SM'), (3, 'M'), (4, 'L'), (5, 'XL'), (6, 'XXL'), (7, 'XXXL'),)
Is_Featured = ((False, "Not a featured."), (True, "Is featured."),)
Delivery_Status = ((1, 'Pending'), (2, 'In Progress'), (3, 'Delivered'), (4, 'Cancelled'),)
VARIANTS = (('Unit', _('Unit')), ('Size', _('Size')), ('Color', _('Color')), ('Size-Color', _('Size-Color')),)
OutStock = (('1', _('2-3 Day')), ('2', _('In Stock')), ('3', _('Out Stock')), ('4', 'Pre-order'),)
Purchase_Status = (("Received", "Received"), ("Partial", "Partial"), ("Pending", "Pending"))
Purchase_Source = (("Web", "Web"), ("Mobile", "Mobile"), )
Order_Status = (('New', 'New'), ('Accepted', 'Accepted'), ('Preparing', 'Preparing'), ('OnShipping', 'OnShipping'),
                ('Completed', 'Completed'), ('Canceled', 'Canceled'), ('Refund', 'Refund'), ('Rejected', 'Rejected'),
                ('Returned', 'Returned'), ('Draft', 'Draft'))
Delivery_By = (('Ydoob', 'Ydoob'), ('Self', 'Self'),)
Commission_System = (('Category', 'Category'), ('DigitalMarketing', 'Digital Marketing'), ('Referral', 'Referral'),
                     ('ShippingRate', 'Shipping Rate'),)
Shipping_Status = (('Active', 'Active'), ('Inactive', 'Inactive'), ('Free', 'Free'),)
Product_Transaction = (('BUY', 'BUY'), ('SELL', 'SELL'), ('REFUND', 'REFUND'))
Payment_Status = (("Pending", "Pending"), ("Complete", "Complete"), ("Partial", "Partial"), ("Other", "Other"),
                  ("Refunded", "Refunded"), ("Failed", "Failed"), ("Abandoned", "Abandoned"), ("Revoked", "Revoked"),
                  ("Preapproval", "Preapproval"), ("Cancelled", "Cancelled"), ("Subscription", "Subscription"),)
Payment_Methods = (("Online Payment", "Online Payment"), ("Cash on Delivery", "Cash on Delivery"),)
Payment_Gateway = (('COD', 'COD'), ('PayTabs', 'PayTabs'), ('Paymob', 'Paymob'))
Invoice_Status = [('CURRENT', 'CURRENT'), ('OVERDUE', 'OVERDUE'), ('PAID', 'PAID'), ]

Invoice_CreatedBy = [('CUSTOMER', 'CUSTOMER'), ('ADMIN', 'ADMIN'), ('STAFF', 'STAFF'), ('VENDOR', 'VENDOR'),
                     ('SHIPPING', 'SHIPPING'), ]
Transaction_Money_Type = (("Buy", _("Buy")), ("Sell", _("Sell")), ('Refund', _('Refund')), ('Withdraw', _('Withdraw')),
                          ('Deposit', _('Deposit')), ('Transfer', _('Transfer')), ('Commission', _('Commission')),
                          ('Shipping', _('Shipping')), ('Referral', _('Referral')), ('Rent', _('Rent')),
                          ('Leasing', _('Leasing')), ('Salary', _('Salary')), ('Cost', _('Cost')),
                          ('Leasing Cost', _('Leasing Cost')), ('Expenses', _('Expenses')),
                          ('Timesheet', _('Timesheet')),)

Transaction_Money_Mode = (("Cash", _("Cash")), ("Credit", _("Credit")), ('Debit', _('Debit')), ('Wallet', _('Wallet')),
                          ('Treasury', _('Treasury')), ("Pending", _("Pending")))
Transaction_Method = (("Cash", _("Cash")), ("Visa", _("Visa")), ('Wallet', _('Wallet')), ('Cheque', _('Cheque')),
                      ('Bank', _('Bank')),)
Transaction_Money_Status = (("Pending", _("Pending")), ('Partial', _('Partial')), ("Complete", _("Complete")),
                            ('Failed', _('Failed')),)
Transaction_Money_Category = (("Income", _("Income")), ("Expense", _("Expense")),)
Transaction_Product_Type = (("Buy", _("Buy")), ("Sell", _("Sell")), ('Refund', _('Refund')),)
Transaction_percent_type = (("1", 65), ("2", 3), ("3", 5),)

Duration_Type = (('Days', 'Days'), ('Weeks', 'Weeks'), ('Months', 'Months'), ('Years', 'Years'),)
Wallet_Mode = (("Administrator", _("Administrator")), ("Auditor", _("Auditor")), ("Accountant", _("Accountant")),
               ("User", _("User")),)
Current_App = (("Digithup", _("Digithup")),
("Classified", _("Classified")), ("Jobs", _("Jobs")),
               ("Other", _("Other")),)
Barcode_Class = (("ean13", _("ean13")), ("code128", _("code128")), ("code39", _("code39")), ("code93", _("code93")),
                 ("code11", _("code11")), ("msi", _("msi")), ("codabar", _("codabar")), ("upc", _("upc")),
                 ("ean8", _("ean8")), ("upce", _("upce")), ("i2of5", _("i2of5")), ("ext_i2of5", _("ext_i2of5")),
                 ("postnet", _("postnet")), ("fim", _("fim")), ("itf14", _("itf14")), ("pzn", _("pzn")),
                 ("plessey", _("plessey")), ("msi10", _("msi10")), ("msi11", _("msi11")), ("msi1010", _("msi1010")),
                 ("msi1110", _("msi1110")), ("pharmacode", _("pharmacode")), ("code32", _("code32")),
                 ("code39ext", _("code39ext")), ("itf6", _("itf6")), ("itf16", _("itf16")), ("gs1_128", _("gs1_128")),
                 ("gs1_128_hr", _("gs1_128_hr")), ("gs1_128_hrt", _("gs1_128_hrt")), ("gs1_128_lgt", _("gs1_128_lgt")),
                 ("gs1_128_lgto", _("gs1_128_lgto")), ("gs1_128_lgts", _("gs1_128_lgts")),
                 ("gs1_128_exp", _("gs1_128_exp")), ("telepen", _("telepen")), ("telepen_num", _("telepen_num")),
                 ("pharmacode2", _("pharmacode2")), ("code25", _("code25")), ("code25_iata", _("code25_iata")),
                 ("code25_matrix", _("code25_matrix")), ("code25_interleaved", _("code25_interleaved")),
                 ("code25_industrial", _("code25_industrial")), ("code39_pmod", _("code39_pmod")),
                 ("code39_mod43", _("code39_mod43")), ("code93ext", _("code93ext")), ("code93_pmod", _("code93_pmod")),
                 ("bcs_code128", _("bcs_code128")), ("bcs_code128_pmod", _("bcs_code128_pmod")),
                 ("bcs_code128_mod43", _("bcs_code128_mod43")), ("bcs_code39", _("bcs_code39")),
                 ("bcs_code39_pmod", _("bcs_code39_pmod")), ("bcs_code39_mod43", _("bcs_code39_mod43")),
                 ("bcs_code93", _("bcs_code93")), ("bcs_code93_pmod", _("bcs_code93_pmod")),
                 ("bcs_code93_mod43", _("bcs_code93_mod43")), ("bcs_datamatrix", _("bcs_datamatrix")),
                 ("bcs_ean", _("bcs_ean")), ("bcs_ean2", _("bcs_ean2")), ("bcs_ean5", _("bcs_ean5")),
                 ("bcs_ean8", _("bcs_ean8")), ("bcs_ean13", _("bcs_ean13")), ("bcs_ean14", _("bcs_ean14")),
                 ("bcs_ean128", _("bcs_ean128")), ("bcs_ean128_pmod", _("bcs_ean128_pmod")),
                 ("bcs_ean128_mod43", _("bcs_ean128_mod43")), ("bcs_gs1", _("bcs_gs1")),
                 ("bcs_gs1_pmod", _("bcs_gs1_pmod")), ("bcs_gs1_mod43", _("bcs_gs1_mod43")),
                 ("bcs_itf14", _("bcs_itf14")), ("bcs_itf", _("bcs_itf")), ("bcs_itf_pmod", _("bcs_itf_pmod")),
                 ("bcs_itf_mod43", _("bcs_itf_mod43")), ("bcs_msi", _("bcs_msi")), ("bcs_msi_pmod", _("bcs_msi_pmod")),
                 ("bcs_msi_mod11", _("bcs_msi_mod11")), ("bcs_msi_mod1010", _("bcs_msi_mod1010")),
                 ("bcs_msi_mod1110", _("bcs_msi_mod1110")), ("bcs_pharmacode", _("bcs_pharmacode")),
                 ("bcs_pharmacode2", _("bcs_pharmacode2")), ("bcs_pzn", _("bcs_pzn")), ("bcs_pzn8", _("bcs_pzn8")),
                 ("bcs_rss14", _("bcs_rss14")), ("bcs_rss14_stacked", _("bcs_rss14_stacked")),
                 ("bcs_rss14_stacked_omni", _("bcs_rss14_stacked_omni")),
                 ("bcs_rss14_truncated", _("bcs_rss14_truncated")), ("bcs_rss14_limited", _("bcs_rss14_limited")),
                 ("bcs_rss14_expanded", _("bcs_rss14_expanded")),
                 ("bcs_rss14_expanded_stacked", _("bcs_rss14_expanded_stacked")),
                 ("bcs_rss14_expanded_stacked_omni", _("bcs_rss14_expanded_stacked_omni")),
                 ("bcs_rss14_expanded_stacked_omni", _("bcs_rss14_expanded_stacked_omni")),
                 ("bcs_rss14_lim_stack", _("bcs_rss14_lim_stack")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),
                 ("bcs_rss14_exp_stack", _("bcs_rss14_exp_stack")),
                 ("bcs_rss14_exp_stack_omni", _("bcs_rss14_exp_stack_omni")),
                 ("bcs_rss14_exp_stack_omni", _("bcs_rss14_exp_stack_omni")),
                 ("bcs_rss14_trunc_stack", _("bcs_rss14_trunc_stack")),
                 ("bcs_rss14_trunc_stack_omni", _("bcs_rss14_trunc_stack_omni")),
                 ("bcs_rss14_trunc_stack_omni", _("bcs_rss14_trunc_stack_omni")),
                 ("bcs_rss14_lim_stack", _("bcs_rss14_lim_stack")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),
                 ("bcs_rss14_lim_stack_omni", _("bcs_rss14_lim_stack_omni")),)

########################## Podcast ############################
Video_Source = (('Youtube', 'Youtube'), ('Vimeo', 'Vimeo'), ('Self', 'Self'),)

########################## Employee ############################
Absent_Type = (('Sick', 'Sick'), ('Vacation', 'Vacation'), ('Other', 'Other'),)
Absent_Status = (('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'),)


########################## Notification  ############################
Notification_CHOICES = (("New", _("New")), ("Message", _("Message")), ("Application", _("Application")),
                        ("NewR egistration", _("New Registration")), ("New Vendor", _("NewV endor")),
                        ("Payment", _("Payment")), ("Order", _("Order")), ("Shipping", _("Shipping")),
                        ("Delivery", _("Delivery")), ("Other", _("Other")), ("Reservation", _("Reservation")),)

################### MEMBERSHIP ##############################
MEMBERSHIP_CHOICES = (

    ('Free', 'Free Membership'), ('Paid', 'Paid Membership'), ('PromoCode', 'PromoCode Membership'),
    ('NoMembership', 'No Membership'), ('Expired Membership', 'Expired Membership'), ('Default', 'Default Membership'),
    ('Admin', 'Admin Membership'), ('user', 'user Membership'),

)
PERIOD_DURATION = (('Days', ('Days')), ('Week', 'Week'), ('Months', 'Months'), ('Quarter', 'Quarter'),
                   ('Years', 'Years'),)
Subscription_Status = (("New", _("New")), ("Accepted", _("Accepted")), ("Rejected", _("Rejected")),
                       ("Canceled", _("Canceled")), ("Completed", _("Completed")), ("Expired", _("Expired")),
                       ("Suspend", _("Suspend")),)

################### ClassifiedAd ##############################

REPORT_TYPES = (('Spam', 'Spam'), ('Inappropriate', 'Inappropriate'),
                ('Fraud', 'Fraud'), ('Scam', 'Scam'), ('Duplicate', 'Duplicate'), ('Other', 'Other'),)
JobProvider_Type = ( ('Company', _("Company")),
                    ('institution', _("Institution")),  ('Freelance Document', _("Freelance Document")),)

Job_Offer_Status = (('Accepted', 'Accepted'), ('Rejected', 'Rejected'), ('Pending', 'Pending'), )
Job_Progress_Status =    (('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed'),
                        ('On Hold', 'On Hold'), ('Cancelled', 'Cancelled'),('Assigned', 'Assigned'),)
################### Blog ##############################
Service_Type = (('Service', 'Service'), ('Work', 'Work'), ('Product', 'Product'), ('Project', 'Project'),
                ('Portfolio', 'Portfolio'), ('Other', 'Other'))
Service_Status = (('Active', 'Active'), ('Waiting', 'Waiting for activation'), ('Inactive', 'Inactive'),)
Featured_Status = (('Active', 'Active'), ('Inactive', 'Inactive'),)
MultiFile_Type = (('image', 'image'), ('hero', 'hero'), ('video', 'video'), ('cover', 'cover'), ('file', 'file'),
                  ('Other', 'Other'))
Banners_Position = (('Top Left', 'Top Left'), ('Top Middle', 'Top Middle'), ('Top Right', 'Top Right'),
                    ('Middle Left', 'Middle Left'), ('Middle Right', 'Middle Right'), ('Bottom Left', 'Bottom Left'),
                    ('Bottom Middle', 'Bottom Middle'), ('Bottom Right', 'Bottom Right'),
                    ('Collection Sidebar', 'Collection Sidebar'), ('Categories Top', 'Categories Top'),
                    ('Categories Sidebar', 'Categories Sidebar'),)

################### User ##############################
User_Position = (('Writer', 'Writer'), ('Lawyer', 'Lawyer'), ('Clients', 'Clients'), ('Co-founder', 'Co-founder'),
                 ('Developer', 'Developer'), ('Admin', 'Admin'), ('SuperAdmin', 'SuperAdmin'), ('Editor', 'Editor'),
                 ('Moderator', 'Moderator'), ('Member', 'Member'), ('Guest', 'Guest'))
Access_Level = (('Customer', 'Customer') ,('Member', 'Member'),
               ('Vendor', 'Vendor'), ('Shipping', 'Shipping'),
               ('Employee', 'Employee'), ('Manager', 'Manager'),('Staff', 'Staff'), ('Accountant', 'Accountant'), ('Owner', 'Owner'),
                ('Partner', 'Partner'),  ('Admin', 'Admin'),('SuperAdmin', 'SuperAdmin'),)
User_Status = (('Active', 'Active'), ('Inactive', 'Inactive'), ('Suspend', 'Suspend'), ('Banned', 'Banned'),)
User_Title = (('Mr', 'Mr'), ('Miss', 'Miss'), ('Dr', 'Dr'), ('Prof', 'Prof'), ('Major General', 'Major General'))

############### Clients Helper ###############
Client_Type = (("Supplier", _("Supplier")), ("Client", _("Client")), ("Major", _("Major  Client")),
               ("walkIn", _("walkIn")), ("Vendor", _("Vendor")), ("Contractor", _("Contractor")),
               ("Company", _("Company")), ("Owner", _("Owner")), ("Attendees", _("Attendees")), ("Other", _("Other")),)

Employee_Type = (("Employee", _("Employee")), ("Accountant", _("Accountant")), ("Moderator", _("Moderator")),
                 ("Manager", _("Manager")), ("Owner", _("Owner")), ("Partner", _("Partner")),)
Address_Type = (('Home', 'Home'), ('Business', 'Business'),)
Employee_Overtime_Type = (('Hourly', _('Hourly')), ('Daily', _('Daily')), ('Weekly', _('Weekly')),
                          ('Monthly', _('Monthly')),)
Company_Type = (('Clinic', 'Clinic'), ('ThirdParty', 'ThirdParty'), ('Partner', 'Partner'), ('Other', 'Other'),)

############### CRM Helper ###############
Cost_Type = (('Fixed', 'Fixed'), ('Variable', 'Variable'), ('Once', 'Once'), ('Monthly', 'Monthly'),
             ('Yearly', 'Yearly'), ('Daily', 'Daily'), ('Hourly', 'Hourly'), ('Other', 'Other'),)

Project_Type = (('Programming', 'Programming'), ('Design', 'Design'), ('Marketing', 'Marketing'),
                ('Management', 'Management'), ('Project', 'Project'), ('Task', 'Task'), ('Event', 'Event'),
                ('Other', 'Other'),)
