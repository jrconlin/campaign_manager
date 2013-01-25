<!doctype html>
<%
    from campaign.util import strToUTC
    from time import (time, strftime, gmtime)
    import json

    vers = pageargs.get('version', 1)
    land = pageargs.get('landing', '/author/%s/' % vers)
    config = pageargs.get('config', {})
    announcements = pageargs.get('announcements', [])
    author = pageargs.get('author', 'UNKNOWN')
    settings = pageargs.get('settings', {})

    time_fmt = '%a, %d %b %Y - %H:%M:%S GMT'

    current_rel = int(settings.get('form.current_release', '17'))
    start_adj = int(settings.get('form.start_adj', '4'))
    # Firefox 17 released on 30 Nov 2012 00:00:00 UTC
    current_rel_date = strToUTC(settings.get('form.current_release_date',
        'Mon 30 Nov 2012 00:00:00 UTC'))
    # 6 weeks =
    release_period = int(pageargs.get('form.release_period', 3628800))
    nowstr = strftime(time_fmt, gmtime())
    nowsec = time()

    ver_adj = (int(nowsec) - current_rel_date) / release_period
    current_rel = current_rel + ver_adj
    start_rel = current_rel - start_adj
    max_rel = current_rel + 4

    campaign_end = int(nowsec / 86400) * 86400 + \
        int(pageargs.get('default.campaign_length', 14)) * 86400
    campaign_end_str = strftime(time_fmt, gmtime(campaign_end))

    ver_adj = (int(nowsec) - current_rel_date) / release_period
    current_rel = current_rel + ver_adj
    start_rel = current_rel - start_adj
    max_rel = current_rel + 4

%>
<html>
<head>
<title>Welcome ${author}</title>
<link rel="stylesheet" type="text/css" href="/static/style.css" />
<link rel="stylesheet" type="text/css" href="http://www.mozilla.org/tabzilla/media/css/tabzilla.css" />
</head>
<body>
<!-- This had <blank>ing better not be user facing, so skipping tabzilla -->
<!--a href="http://www.mozilla.org/" id="tabzilla">mozilla</a--!>
<header>
<h1>Campaign Admin Panel</h1>
<div class="control">
<button class="button logout">Log out</button>
<!-- yep, this should be a REST get and display call. -->
</header>
<form id="new_item" action="${land}" method="POST">
    <h2>New Item</h2>
    <label for="ctitle">Campaign Name:<input name="ctitle" /></label>
    <input type="hidden" name="author" value="${author}" />
    <span class="hidden" id="alert"><b>Caution:</b> Campaign conflicts with highlited campaigns.</span>
<fieldset class="times">
<legend>When to show?</legend>
<span class="priority"><label for="priority">Priority(0=lowest):</label><input type="number" name="priority" value="0" /></span>
<label for="start_time">Start time:</label><input type="datetime-local" name="start_time" value="" placeholder="${nowstr}"/>
<label for="idle_time">Idle time(days):</label><input type="number" name="idle_time" value="0" />
<label for="end_time">Projected End time:</label><input type="datetime-local" name="end_time" value="${campaign_end_str}" placeholder="${campaign_end_str}" readonly />
</fieldset>
<fieldset class="note">
<legend>What should they see?</legend>
<label for="title">Title:</label><input type="text" name="title" placeholder="Free Puppies!"/>
<label for="dest_url">Destination URL:</label><input type="text" name="dest_url" placeholder="http://example.org/"/>
<label for="body">Body:</label><input type="text" name="body" placeholder="Who doesn't love free puppies?"/>
</fieldset>
<fieldset class="locale">
<legend>Who should see?</legend>
<label for="lang">Language:</label><select name="lang" length="2"/>
<option value="all" selected>All</option>
<option value="ab">Abkhazian</option>
<option value="aa">Afar</option>
<option value="af">Afrikaans</option>
<option value="sq">Albanian</option>
<option value="am">Amharic</option>
<option value="ar">Arabic</option>
<option value="an">Aragonese</option>
<option value="hy">Armenian</option>
<option value="as">Assamese</option>
<option value="ay">Aymara</option>
<option value="az">Azerbaijani</option>
<option value="ba">Bashkir</option>
<option value="eu">Basque</option>
<option value="bn">Bengali(Bangla)</option>
<option value="dz">Bhutani</option>
<option value="bh">Bihari</option>
<option value="bi">Bislama</option>
<option value="br">Breton</option>
<option value="bg">Bulgarian</option>
<option value="my">Burmese</option>
<option value="be">Byelorussian(Belarusian)</option>
<option value="km">Cambodian</option>
<option value="ca">Catalan</option>
<option value="zh">Chinese(Simplified)</option>
<option value="zh">Chinese(Traditional)</option>
<option value="co">Corsican</option>
<option value="hr">Croatian</option>
<option value="cs">Czech</option>
<option value="da">Danish</option>
<option value="nl">Danishutch</option>
<option value="en">English</option>
<option value="eo">Esperanto</option>
<option value="et">Estonian</option>
<option value="fo">Faeroese</option>
<option value="fa">Farsi</option>
<option value="fj">Fiji</option>
<option value="fi">Finnish</option>
<option value="fr">French</option>
<option value="fy">Frisian</option>
<option value="gl">Galician</option>
<option value="gd">Gaelic(Scottish)</option>
<option value="gv">Gaelic(Manx)</option>
<option value="ka">Georgian</option>
<option value="de">German</option>
<option value="el">Greek</option>
<option value="kl">Greenlandic</option>
<option value="gn">Guarani</option>
<option value="gu">Gujarati</option>
<option value="ht">Haitian(Creole)</option>
<option value="ha">Hausa</option>
<option value="he">Hebrew</option>
<option value="iw">Hebrew</option>
<option value="hi">Hindi</option>
<option value="hu">Hungarian</option>
<option value="is">Icelandic</option>
<option value="io">Ido</option>
<option value="id">Indonesian</option>
<option value="in">Indonesian</option>
<option value="ia">Interlingua</option>
<option value="ie">Interlingue</option>
<option value="iu">Inuktitut</option>
<option value="ik">Inupiak</option>
<option value="ga">Irish</option>
<option value="it">Italian</option>
<option value="ja">Japanese</option>
<option value="jv">Javanese</option>
<option value="kn">Kannada</option>
<option value="ks">Kashmiri</option>
<option value="kk">Kazakh</option>
<option value="rw">Kinyarwanda(Ruanda)</option>
<option value="ky">Kirghiz</option>
<option value="rn">Kirundi(Rundi)</option>
<option value="ko">Korean</option>
<option value="ku">Kurdish</option>
<option value="lo">Laothian</option>
<option value="la">Latin</option>
<option value="lv">Latvian(Lettish)</option>
<option value="li">Limburgish(Limburger)</option>
<option value="ln">Lingala</option>
<option value="lt">Lithuanian</option>
<option value="mk">Macedonian</option>
<option value="mg">Malagasy</option>
<option value="ms">Malay</option>
<option value="ml">Malayalam</option>
<option value="mt">Maltese</option>
<option value="mi">Maori</option>
<option value="mr">Marathi</option>
<option value="mo">Moldavian</option>
<option value="mn">Mongolian</option>
<option value="na">Nauru</option>
<option value="ne">Nepali</option>
<option value="no">Norwegian</option>
<option value="oc">Occitan</option>
<option value="or">Oriya</option>
<option value="om">Oromo(Afan,Galla)</option>
<option value="ps">Pashto(Pushto)</option>
<option value="pl">Polish</option>
<option value="pt">Portuguese</option>
<option value="pa">Punjabi</option>
<option value="qu">Quechua</option>
<option value="rm">Rhaeto-Romance</option>
<option value="ro">Romanian</option>
<option value="ru">Russian</option>
<option value="sm">Samoan</option>
<option value="sg">Sangro</option>
<option value="sa">Sanskrit</option>
<option value="sr">Serbian</option>
<option value="sh">Serbo-Croatian</option>
<option value="st">Sesotho</option>
<option value="tn">Setswana</option>
<option value="sn">Shona</option>
<option value="ii">Sichuan Yii</option>
<option value="sd">Sindhi</option>
<option value="si">Sinhalese</option>
<option value="ss">Siswati</option>
<option value="sk">Slovak</option>
<option value="sl">Slovenian</option>
<option value="so">Somali</option>
<option value="es">Spanish</option>
<option value="su">Sundanese</option>
<option value="sw">Swahili(Kiswahili)</option>
<option value="sv">Swedish</option>
<option value="tl">Tagalog</option>
<option value="tg">Tajik</option>
<option value="ta">Tamil</option>
<option value="tt">Tatar</option>
<option value="te">Telugu</option>
<option value="th">Thai</option>
<option value="bo">Tibetan</option>
<option value="ti">Tigrinya</option>
<option value="to">Tonga</option>
<option value="ts">Tsonga</option>
<option value="tr">Turkish</option>
<option value="tk">Tibetanurkmen</option>
<option value="tw">Twi</option>
<option value="ug">Uighur</option>
<option value="uk">Ukrainian</option>
<option value="ur">Urdu</option>
<option value="uz">Uzbek</option>
<option value="vi">Vietnamese</option>
<option value="vo">Volap&#376;k</option>
<option value="wa">Wallon</option>
<option value="cy">Welsh</option>
<option value="wo">Wolof</option>
<option value="xh">Xhosa</option>
<option value="yi">Yiddish</option>
<option value="ji">Yiddish</option>
<option value="yo">Yoruba</option>
<option value="zu">Zulu</option>
</select>-
<label for="locale">Locale:</label><select name="locale">
<option value="all" selected>All</option>
<option value="AF">Afghanistan</option>
<option value="AX">&#197;land Islands</option>
<option value="AL">Albania</option>
<option value="DZ">Algeria</option>
<option value="AS">American Samoa</option>
<option value="AD">Andorra</option>
<option value="AO">Angola</option>
<option value="AI">Anguilla</option>
<option value="AQ">Antarctica</option>
<option value="AG">Antigua and Barbuda</option>
<option value="AR">Argentina</option>
<option value="AM">Armenia</option>
<option value="AW">Aruba</option>
<option value="AU">Australia</option>
<option value="AT">Austria</option>
<option value="AZ">Azerbaijan</option>
<option value="BS">Bahamas</option>
<option value="BH">Bahrain</option>
<option value="BD">Bangladesh</option>
<option value="BB">Barbados</option>
<option value="BY">Belarus</option>
<option value="BE">Belgium</option>
<option value="BZ">Belize</option>
<option value="BJ">Benin</option>
<option value="BM">Bermuda</option>
<option value="BT">Bhutan</option>
<option value="BO">Bolivia, Plurinational State of</option>
<option value="BQ">Bonaire, Sint Eustatius and Saba</option>
<option value="BA">Bosnia and Herzegovina</option>
<option value="BW">Botswana</option>
<option value="BV">Bouvet Island</option>
<option value="BR">Brazil</option>
<option value="IO">British Indian Ocean Territory</option>
<option value="BN">Brunei Darussalam</option>
<option value="BG">Bulgaria</option>
<option value="BF">Burkina Faso</option>
<option value="BI">Burundi</option>
<option value="KH">Cambodia</option>
<option value="CM">Cameroon</option>
<option value="CA">Canada</option>
<option value="CV">Cape Verde</option>
<option value="KY">Cayman Islands</option>
<option value="CF">Central African Republic</option>
<option value="TD">Chad</option>
<option value="CL">Chile</option>
<option value="CN">China</option>
<option value="CX">Christmas Island</option>
<option value="CC">Cocos (Keeling) Islands</option>
<option value="CO">Colombia</option>
<option value="KM">Comoros</option>
<option value="CG">Congo</option>
<option value="CD">Congo, the Democratic Republic of the</option>
<option value="CK">Cook Islands</option>
<option value="CR">Costa Rica</option>
<option value="CI">C&#244;te d'Ivoire</option>
<option value="HR">Croatia</option>
<option value="CU">Cuba</option>
<option value="CW">Cura&#231;ao</option>
<option value="CY">Cyprus</option>
<option value="CZ">Czech Republic</option>
<option value="DK">Denmark</option>
<option value="DJ">Djibouti</option>
<option value="DM">Dominica</option>
<option value="DO">Dominican Republic</option>
<option value="EC">Ecuador</option>
<option value="EG">Egypt</option>
<option value="SV">El Salvador</option>
<option value="GQ">Equatorial Guinea</option>
<option value="ER">Eritrea</option>
<option value="EE">Estonia</option>
<option value="ET">Ethiopia</option>
<option value="FK">Falkland Islands (Malvinas)</option>
<option value="FO">Faroe Islands</option>
<option value="FJ">Fiji</option>
<option value="FI">Finland</option>
<option value="FR">France</option>
<option value="GF">French Guiana</option>
<option value="PF">French Polynesia</option>
<option value="TF">French Southern Territories</option>
<option value="GA">Gabon</option>
<option value="GM">Gambia</option>
<option value="GE">Georgia</option>
<option value="DE">Germany</option>
<option value="GH">Ghana</option>
<option value="GI">Gibraltar</option>
<option value="GR">Greece</option>
<option value="GL">Greenland</option>
<option value="GD">Grenada</option>
<option value="GP">Guadeloupe</option>
<option value="GU">Guam</option>
<option value="GT">Guatemala</option>
<option value="GG">Guernsey</option>
<option value="GN">Guinea</option>
<option value="GW">Guinea-Bissau</option>
<option value="GY">Guyana</option>
<option value="HT">Haiti</option>
<option value="HM">Heard Island and McDonald Islands</option>
<option value="VA">Holy See (Vatican City State)</option>
<option value="HN">Honduras</option>
<option value="HK">Hong Kong</option>
<option value="HU">Hungary</option>
<option value="IS">Iceland</option>
<option value="IN">India</option>
<option value="ID">Indonesia</option>
<option value="IR">Iran, Islamic Republic of</option>
<option value="IQ">Iraq</option>
<option value="IE">Ireland</option>
<option value="IM">Isle of Man</option>
<option value="IL">Israel</option>
<option value="IT">Italy</option>
<option value="JM">Jamaica</option>
<option value="JP">Japan</option>
<option value="JE">Jersey</option>
<option value="JO">Jordan</option>
<option value="KZ">Kazakhstan</option>
<option value="KE">Kenya</option>
<option value="KI">Kiribati</option>
<option value="KP">Korea, Democratic People's Republic of</option>
<option value="KR">Korea, Republic of</option>
<option value="KW">Kuwait</option>
<option value="KG">Kyrgyzstan</option>
<option value="LA">Lao People's Democratic Republic</option>
<option value="LV">Latvia</option>
<option value="LB">Lebanon</option>
<option value="LS">Lesotho</option>
<option value="LR">Liberia</option>
<option value="LY">Libya</option>
<option value="LI">Liechtenstein</option>
<option value="LT">Lithuania</option>
<option value="LU">Luxembourg</option>
<option value="MO">Macao</option>
<option value="MK">Macedonia, The Former Yugoslav Republic of</option>
<option value="MG">Madagascar</option>
<option value="MW">Malawi</option>
<option value="MY">Malaysia</option>
<option value="MV">Maldives</option>
<option value="ML">Mali</option>
<option value="MT">Malta</option>
<option value="MH">Marshall Islands</option>
<option value="MQ">Martinique</option>
<option value="MR">Mauritania</option>
<option value="MU">Mauritius</option>
<option value="YT">Mayotte</option>
<option value="MX">Mexico</option>
<option value="FM">Micronesia, Federated States of</option>
<option value="MD">Moldova, Republic of</option>
<option value="MC">Monaco</option>
<option value="MN">Mongolia</option>
<option value="ME">Montenegro</option>
<option value="MS">Montserrat</option>
<option value="MA">Morocco</option>
<option value="MZ">Mozambique</option>
<option value="MM">Myanmar</option>
<option value="NA">Namibia</option>
<option value="NR">Nauru</option>
<option value="NP">Nepal</option>
<option value="NL">Netherlands</option>
<option value="NC">New Caledonia</option>
<option value="NZ">New Zealand</option>
<option value="NI">Nicaragua</option>
<option value="NE">Niger</option>
<option value="NG">Nigeria</option>
<option value="NU">Niue</option>
<option value="NF">Norfolk Island</option>
<option value="MP">Northern Mariana Islands</option>
<option value="NO">Norway</option>
<option value="OM">Oman</option>
<option value="PK">Pakistan</option>
<option value="PW">Palau</option>
<option value="PS">Palestinian Territory, Occupied</option>
<option value="PA">Panama</option>
<option value="PG">Papua New Guinea</option>
<option value="PY">Paraguay</option>
<option value="PE">Peru</option>
<option value="PH">Philippines</option>
<option value="PN">Pitcairn</option>
<option value="PL">Poland</option>
<option value="PT">Portugal</option>
<option value="PR">Puerto Rico</option>
<option value="QA">Qatar</option>
<option value="RE">R&#233;union</option>
<option value="RO">Romania</option>
<option value="RU">Russian Federation</option>
<option value="RW">Rwanda</option>
<option value="BL">Saint Barth&#233;lemy</option>
<option value="SH">Saint Helena, Ascension and Tristan da Cunha</option>
<option value="KN">Saint Kitts and Nevis</option>
<option value="LC">Saint Lucia</option>
<option value="MF">Saint Martin (French part)</option>
<option value="PM">Saint Pierre and Miquelon</option>
<option value="VC">Saint Vincent and the Grenadines</option>
<option value="WS">Samoa</option>
<option value="SM">San Marino</option>
<option value="ST">Sao Tome and Principe</option>
<option value="SA">Saudi Arabia</option>
<option value="SN">Senegal</option>
<option value="RS">Serbia</option>
<option value="SC">Seychelles</option>
<option value="SL">Sierra Leone</option>
<option value="SG">Singapore</option>
<option value="SX">Sint Maarten (Dutch part)</option>
<option value="SK">Slovakia</option>
<option value="SI">Slovenia</option>
<option value="SB">Solomon Islands</option>
<option value="SO">Somalia</option>
<option value="ZA">South Africa</option>
<option value="GS">South Georgia and the South Sandwich Islands</option>
<option value="SS">South Sudan</option>
<option value="ES">Spain</option>
<option value="LK">Sri Lanka</option>
<option value="SD">Sudan</option>
<option value="SR">Suriname</option>
<option value="SJ">Svalbard and Jan Mayen</option>
<option value="SZ">Swaziland</option>
<option value="SE">Sweden</option>
<option value="CH">Switzerland</option>
<option value="SY">Syrian Arab Republic</option>
<option value="TW">Taiwan, Province of China</option>
<option value="TJ">Tajikistan</option>
<option value="TZ">Tanzania, United Republic of</option>
<option value="TH">Thailand</option>
<option value="TL">Timor-Leste</option>
<option value="TG">Togo</option>
<option value="TK">Tokelau</option>
<option value="TO">Tonga</option>
<option value="TT">Trinidad and Tobago</option>
<option value="TN">Tunisia</option>
<option value="TR">Turkey</option>
<option value="TM">Turkmenistan</option>
<option value="TC">Turks and Caicos Islands</option>
<option value="TV">Tuvalu</option>
<option value="UG">Uganda</option>
<option value="UA">Ukraine</option>
<option value="AE">United Arab Emirates</option>
<option value="GB">United Kingdom</option>
<option value="US">United States</option>
<option value="UM">United States Minor Outlying Islands</option>
<option value="UY">Uruguay</option>
<option value="UZ">Uzbekistan</option>
<option value="VU">Vanuatu</option>
<option value="VE">Venezuela, Bolivarian Republic of</option>
<option value="VN">Viet Nam</option>
<option value="VG">Virgin Islands, British</option>
<option value="VI">Virgin Islands, U.S.</option>
<option value="WF">Wallis and Futuna</option>
<option value="EH">Western Sahara</option>
<option value="YE">Yemen</option>
<option value="ZM">Zambia</option>
<option value="ZW">Zimbabwe</option>
</select>
</fieldset>
<fieldset class="platform">
<legend>On what?</legend>
<label for="product">Product:</label><input type="text" name="product" value="${settings.get("form.product", "android")}" />
<label for="platform">Platform:</label>
<select name="platform">
    <option selected>all</option>
    <% platforms = settings.get('form.platforms',
        'armeabi-v7a, armeabi, mips, x86').split(',')
%>
% for platform in platforms:
<% platform = platform.strip() %>
    <option value="${platform}">${platform}</option>
% endfor
</select>
<label for="channel">Channel:</label>
<select name="channel">
    <option value="all" selected>all</option>
    <option value="firefox">firefox</option>
    <option value="beta">beta</option>
    <option value="aurora">aurora</option>
    <option value="nightly">nightly</option>
    <option value="dev">dev</option>
</select>
<label for="version">Version:</label>
<select name="version">
<option value="all" selected>all</option>
% for v in xrange(start_rel, max_rel):
% if v == current_rel:
<option value="${v}" class="current">${v}*</option>
% else:
<option value="${v}">${v}</option>
% endif
% endfor
</select>
</fieldset>
<button class="button" type="submit">Create</button>
<button class="button" type="clear">Clear</button>
</form>
<div id="existing">
<h2>Existing Records</h2>
<div class="control">
<button class="button" id="select_all" name="select_all">Select all</button>
<button class="button" id="clear" name="clear_all">Clear selected</button>
<button class="button" id="delete" name="delete">Delete Selected</button>
</div>
<table id="data">
<tr class="head row">
<th class="delete">Delete?</th>
<th class="id">ID</th>
<th class="priority">Priority</th>
<th class="created">Created</th>
<th class="start_time">Start Time</th>
<th class="idle_time">Idle Time</th>
<th class="lang">Language</th>
<th class="locale">Locale</th>
<th class="product">Product</th>
<th class="channel">Channel</th>
<th class="version">Version</th>
<th class="platform">Platform</th>
<th class="author">Author</th>
<th class="dest_url">Destination URL</th>
</div>
<%
    time_format = '%a, %d %b %Y - %H:%M:%S GMT'
    %>
    <!-- Wanna guess what ougth to be done as a rest call? hint: -->
%for note in announcements:
<%
    dnote = dict(note);

    if dnote.get('start_time'):
        dnote['start_time'] = strftime(time_format, gmtime(note.get('start_time')))
    else:
        dnote['start_time'] = '<i>Now</i>'
    if dnote.get('end_time'):
        dnote['end_time'] = strftime(time_format, gmtime(note.get('end_time')))
    else:
        dnote['end_time'] = '<i>Forever</i>'
    if not dnote.get('idle_time'):
        dnote['idle_time'] = '<i>None</i>'
    if not dnote.get('lang'):
        dnote['lang'] = '<i>Everyone</i>'
    if not dnote.get('locale'):
        dnote['locale'] = '<i>Everywhere</i>'
    if not dnote.get('channel'):
        dnote['channel'] = '<i>All channels</i>'
    if not dnote.get('platform'):
        dnote['platform'] = '<i>All platforms</i>'
    if not dnote.get('version'):
        dnote['version'] = '<i>All versions</i>'
    anote = json.loads(dnote.get('note','{}'))
    rtitle = dnote.get('title','')
    if not len(rtitle or ''):
        rtitle = dnote.get('id')

%>
<tr class="record row" id="${dnote['id']}"
    data-start_time="${int(note.get('start_time') or 0)}"
    data-end_time="${int(note.get('end_time') or 9999999999)}"
    data-idle_time="${note.get('idle_time') or 0}"
    data-lang="${note.get('lang', "")}"
    data-locale="${note.get('locale', "")}"
    data-product="${note.get('product', "")}"
    data-platform="${note.get('platform', "")}"
    data-channel="${note.get('channel', "")}"
    data-version="${note.get('version', "")}">
<td class="delete"><input type="checkbox" value="${note.get('id')}"></td>
<td class="priority">${dnote['priority']}</td>
<td class="id"><a href="/redirect/${vers}/${dnote['id']}">${rtitle}</a></td>
<td class="created">${strftime(time_format, gmtime(dnote['created']))}</td>
<td class="start_time" >${dnote['start_time']}</td>
<!--td class="end_time" >${dnote['end_time']}</td -->
<td class="idle_time" >${dnote['idle_time']} days</td>
<td class="lang" >${dnote['lang']}</td>
<td class="locale" >${dnote['locale']}</td>
<td class="product" >${dnote['product']}</td>
<td class="channel" >${dnote['channel']}</td>
<td class="version" >${dnote['version']}</td>
<td class="platform" >${dnote['platform']}</td>
<td class="author">${dnote['author']}</td>
<td class="dest_url">${dnote['dest_url']}</td>
</div>
<tr class="row metrics">
    <td></td>
<td colspan="4">
<a href="${dnote['dest_url']}" class="announce">
        <span class="title">${anote.get('title', '')}</span>
        <span class="body">${anote.get('text', '')}</span>
    </a>
<td>
    <td class="metrics" colspan="3">
    <div class="label">Served:</span><b>${dnote.get('served', 0)}</b>
    <div class="label">Clicked:</span><b>${dnote.get('clicks',0)}</b>
</td>
</tr>
%endfor
</table>
<footer>

</footer>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js" type="text/javascript"></script>
<script id='bidjs' src="https://browserid.org/include.js" type="text/javascript"></script>
<script type="text/javascript">
    $(".logout").bind("click", function(e) {
            navigator.id.logout();
            $.ajax({url: "/logout/",
                type: "DELETE",
                contentType: "application/javascript",
                success: function(data, status, xhr) {
                    document.location = "${land}";
                    },
                error: function(xhr, status, error) {
                    console.error(status);
                    console.error(error);
                    $(".logout").disable();
                    }
            });
            });
$("#new_item input").change(function() {
        var dv;
        var sday = 86400000; /* milliseconds in day */
        var conflict = false;
        var errors = [];
        // round to start of day.
        var cstart = Math.floor(Date.now()/sday) * sday;
        var form = document.getElementById('new_item');
        dv = form.start_time.value;
        if (dv) {
            try {
                cstart = Date.parse(dv);
            } catch (e) {}
        }
/*        var cend = 9999999999;
        dv = form.end_time.value;
        if (dv) {
            try {
                cend = Math.floor(Date.parse(dv)/1000);
            } catch (e) {}
        }
        if (cend == 9999999999) {
           errors.push({'id': 0, 'reason': "Campaign is eternal"});
           if (! form.end_time.classList.contains('error')){
               form.end_time.classList.add('error');
           }
        } else {
            form.end_time.classList.remove('error');
        }
 */
        form.start_time.value = new Date(cstart).toUTCString();
        var cend = ((parseInt(form.idle_time.value)|1) * sday) + cstart;
        console.debug(new Date(cend));
        form.end_time.value = (new Date(cend)).toUTCString();
        var rows=document.getElementById('data').getElementsByClassName('record');
        for (var rl = 0; rl < rows.length; rl++){
            var row = rows[rl];
            if (row == undefined) continue;
            var id = row.id;
            var jqi = $('#'+id);
            var start = parseInt(row.dataset.start_time) * 1000;
            var end = parseInt(row.dataset.end_time) * 1000;
            var idle = parseInt(row.dataset.idle_time) || 0;
            var lang = (row.dataset.lang || form.lang.value || "").toLowerCase();
            var locale = (row.dataset.locale || form.locale.value || "").toLowerCase();
            var product = (row.dataset.product || form.product.value).toLowerCase();
            var platform = (row.dataset.platform || form.platform.value).toLowerCase();
            var channel = (row.dataset.channel || form.channel.value).toLowerCase();
            var version = row.dataset.version || form.version.value || "all";
            row.classList.remove('warning');
            console.debug(id, cend, end);
            if (cend <= end &&
                idle >= parseInt(form.idle_time.value || "0") &&
                lang == (form.lang.value || "").toLowerCase() &&
                locale == (form.locale.value || "").toLowerCase() &&
                platform == (form.platform.value || "").toLowerCase() &&
                product == (form.product.value || "").toLowerCase() &&
                channel == (form.channel.value || "").toLowerCase() &&
                version == (form.version.value || "all").toLowerCase()
                ){
                    console.log('bad row', id);
                    errors.push({'id': id,
                        'reason': 'campaign overlaps ' + id});
                    if (!row.classList.contains('warning')){
                        row.classList.add('warning');
                    }
            }
        }
        var warn = document.getElementById('alert');
        if (errors.length) {
            if (warn.classList.contains('hidden')){
                warn.classList.remove('hidden');
            }
            for (var el=0; el < errors.length; el++) {
                console.error(errors[el].reason);
            }
        } else {
            if (!warn.classList.contains('hidden')) {
                warn.classList.add('hidden');
            }
        }

});
$("#bidjs").ready(function() {
        navigator.id.watch({loggedInUser: '${author}',
            onlogin: function() {console.debug('main-login')},
            onlogout: function() {
            // Persona loops on calling onlogout. < Neato.
            //document.location="${land}";
                }});
        $(".logout").click(function(){
            navigator.id.logout();
        });
    });
    $("#delete").click(function() {
        deleteables=[]
        $("#existing .record .delete input").each(function () {
            if (this.checked){
               deleteables.push(this.value);
            }
        });
        console.debug(deleteables);
        $.ajax({url: "${land}",
            type: "POST",
            data: {"delete": deleteables.join()},
            success: function(data, status, xhr) {
                document.location = "${land}";
            },
            error: function(xhr, status, error) {
                alert(error);
            }
        });
    });
</script>
<!--script src="http://www.mozilla.org/tabzilla/media/js/tabzilla.js"></script -->
</html>
