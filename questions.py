from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    key: str
    text: str
    options: list[str]


COUNTRIES = {
    "hy": ["🇺🇸 ԱՄՆ", "🇪🇺 Շենգեն / Եվրոպա", "🇬🇧 Մեծ Բրիտանիա", "🇨🇦 Կանադա", "Այլ"],
    "ru": ["🇺🇸 США", "🇪🇺 Шенген / Европа", "🇬🇧 Великобритания", "🇨🇦 Канада", "Другая"],
    "en": ["🇺🇸 USA", "🇪🇺 Schengen / Europe", "🇬🇧 United Kingdom", "🇨🇦 Canada", "Other"],
}

VISA_TYPES = {
    "hy": ["Տուրիստական", "Ուսանողական", "Աշխատանքային", "Բիզնես", "Հյուրի / այցելության", "Այլ"],
    "ru": ["Туристическая", "Студенческая", "Рабочая", "Бизнес", "Гостевая / визит", "Другое"],
    "en": ["Tourist", "Student", "Work", "Business", "Visitor", "Other"],
}


def normalize_country(country: str) -> str:
    value = country.lower()
    if any(x in value for x in ["usa", "сша", "ամն"]):
        return "usa"
    if any(x in value for x in ["germany", "герм", "գերմ"]):
        return "germany"
    if any(x in value for x in ["france", "франц", "ֆրանս"]):
        return "france"
    if any(x in value for x in ["schengen", "шенген", "շենգեն", "europe", "европа", "եվրոպա"]):
        return "schengen"
    if any(x in value for x in ["kingdom", "велик", "բրիտ"]):
        return "uk"
    if any(x in value for x in ["canada", "канад", "կանադ"]):
        return "canada"
    return "other"


COMMON = {
    "hy": [
        Question("passport", "Ունե՞ք գործող անձնագիր։", ["Այո, վավեր է 1 տարուց ավելի", "Այո, բայց ժամկետը շուտով ավարտվում է", "Ոչ"]),
        Question("citizenship", "Ձեր քաղաքացիությունը։", ["ՀՀ", "ՌԴ", "Վրաստան", "Այլ"]),
        Question("residence", "Ո՞ր երկրում եք այժմ բնակվում։", ["Հայաստան", "Ռուսաստան", "Վրաստան", "Այլ"]),
        Question("age", "Քանի՞ տարեկան եք։", ["Մինչև 18", "18-24", "25-34", "35-49", "50+"]),
        Question("family", "Ձեր ընտանեկան կարգավիճակը։", ["Ամուսնացած եմ", "Ամուսնացած չեմ",]),
        Question("employment", "Ունե՞ք աշխատանք կամ բիզնես։", ["Աշխատանք ունեմ", "Սեփական բիզնես ունեմ", "Ուսանող եմ", "Չեմ աշխատում"]),
        Question("experience", "Որքա՞ն ժամանակ եք աշխատում կամ զբաղվում բիզնեսով։", ["Մինչև 6 ամիս", "6-12 ամիս", "1-3 տարի", "3 տարուց ավելի", "Չեմ աշխատում"]),
        Question("income", "Որքա՞ն է ձեր ամսական եկամուտը։", ["Մինչև $500", "$500-$1000", "$1000-$2000", "$2000-ից ավելի", "Կայուն եկամուտ չունեմ"]),
        Question("taxes", "Կարո՞ղ եք ապացուցել ձեր եկամուտը փաստաթղթերով։", ["Այո, լիարժեք", "Մասամբ", "Ոչ"]),
        Question("bank_statement", "Կարո՞ղ եք ներկայացնել բանկային քաղվածք։", ["Այո, բավարար մնացորդով", "Այո, բայց մնացորդը քիչ է", "Ոչ"]),
        Question("bank_amount", "Մոտավորապես ինչքա՞ն գումար կարող եք ցույց տալ բանկային հաշվին։", ["Մինչև $1000", "$1000-$3000", "$3000-$7000", "$7000-ից ավելի", "Չունեմ"]),
        Question("property", "Ունե՞ք սեփականություն կամ կապեր այդ երկրում։", ["Բնակարան / տուն", "Բիզնես / մեքենա", "Ընտանիք / երեխաներ", "Մի քանի կապ", "Չունեմ"]),
        Question("travel_history", "Նախկինում ճանապարհորդե՞լ եք արտասահման։", ["Այո, շատ անգամ", "Այո, 1-2 անգամ", "Ոչ"]),
        Question("previous_visas", "Նախկինում վիզա ստացե՞լ եք։", ["Այո, մի քանի անգամ", "Այո, 1 անգամ", "Ոչ"]),
        Question("refusals", "Նախկինում վիզայի մերժում ունեցե՞լ եք։", ["Ոչ", "Այո, 1 անգամ", "Այո, մի քանի անգամ"]),
        Question("purpose", "Ձեր ուղևորության նպատակը հստա՞կ է։", ["Այո, շատ հստակ", "Մասամբ", "Ոչ այնքան"]),
        Question("documents", "Որքանո՞վ են պատրաստ փաստաթղթերը։", ["Գրեթե բոլորը պատրաստ են", "Մի մասը պատրաստ է", "Դեռ պատրաստ չեն"]),
        Question("time_to_apply", "Ե՞րբ եք նախատեսում դիմել։", ["Այս շաբաթ", "Այս ամիս", "1-3 ամսվա ընթացքում", "Դեռ չեմ որոշել"]),
    ],
    "ru": [
        Question("passport", "У вас есть действующий загранпаспорт?", ["Да, действует больше 1 года", "Да, но срок скоро заканчивается", "Нет"]),
        Question("citizenship", "Ваше гражданство.", ["Армения", "Россия", "Грузия", "Иран", "Другое"]),
        Question("residence", "В какой стране вы сейчас проживаете?", ["Армения", "Россия", "Грузия", "Европа", "Другое"]),
        Question("age", "Сколько вам лет?", ["До 18", "18-24", "25-34", "35-49", "50+"]),
        Question("family", "Ваше семейное положение.", ["Женат / замужем", "Не женат / не замужем", "Есть дети", "Разведен(а)"]),
        Question("employment", "У вас есть официальная работа или бизнес?", ["Официальная работа", "Собственный бизнес", "Я студент", "Не работаю"]),
        Question("experience", "Как долго вы работаете или ведете бизнес?", ["До 6 месяцев", "6-12 месяцев", "1-3 года", "Более 3 лет", "Не работаю"]),
        Question("income", "Какой у вас ежемесячный доход?", ["До $500", "$500-$1000", "$1000-$2000", "Более $2000", "Нет стабильного дохода"]),
        Question("taxes", "Можете подтвердить доход документами?", ["Да, полностью", "Частично", "Нет"]),
        Question("bank_statement", "Можете предоставить банковскую выписку?", ["Да, с хорошим остатком", "Да, но остаток небольшой", "Нет"]),
        Question("bank_amount", "Примерно какую сумму можете показать на счете?", ["До $1000", "$1000-$3000", "$3000-$7000", "Более $7000", "Нет"]),
        Question("property", "Есть ли собственность или связи со страной проживания?", ["Квартира / дом", "Бизнес / машина", "Семья / дети", "Несколько сильных связей", "Нет"]),
        Question("travel_history", "Вы раньше путешествовали за границу?", ["Да, много раз", "Да, 1-2 раза", "Нет"]),
        Question("previous_visas", "Вы раньше получали визы?", ["Да, несколько раз", "Да, 1 раз", "Нет"]),
        Question("refusals", "У вас были отказы по визам?", ["Нет", "Да, 1 раз", "Да, несколько раз"]),
        Question("purpose", "Цель поездки понятная?", ["Да, очень понятная", "Частично", "Не очень"]),
        Question("documents", "Насколько готовы документы?", ["Почти все готовы", "Часть готова", "Пока не готовы"]),
        Question("time_to_apply", "Когда планируете подаваться?", ["На этой неделе", "В этом месяце", "В течение 1-3 месяцев", "Пока не решил(а)"]),
    ],
    "en": [
        Question("passport", "Do you have a valid passport?", ["Yes, valid for more than 1 year", "Yes, but it expires soon", "No"]),
        Question("citizenship", "Your citizenship.", ["Armenia", "Russia", "Georgia", "Iran", "Other"]),
        Question("residence", "Which country do you currently live in?", ["Armenia", "Russia", "Georgia", "Europe", "Other"]),
        Question("age", "How old are you?", ["Under 18", "18-24", "25-34", "35-49", "50+"]),
        Question("family", "Your family status.", ["Married", "Single", "Have children", "Divorced"]),
        Question("employment", "Do you have official employment or a business?", ["Official employment", "Own business", "I am a student", "Not employed"]),
        Question("experience", "How long have you been working or running your business?", ["Less than 6 months", "6-12 months", "1-3 years", "More than 3 years", "Not employed"]),
        Question("income", "What is your monthly income?", ["Under $500", "$500-$1000", "$1000-$2000", "More than $2000", "No stable income"]),
        Question("taxes", "Can you prove your income with documents?", ["Yes, fully", "Partly", "No"]),
        Question("bank_statement", "Can you provide a bank statement?", ["Yes, with good balance", "Yes, but balance is low", "No"]),
        Question("bank_amount", "Approximate bank balance you can show?", ["Under $1000", "$1000-$3000", "$3000-$7000", "More than $7000", "None"]),
        Question("property", "Do you have property or ties in your country of residence?", ["Apartment / house", "Business / car", "Family / children", "Several strong ties", "No"]),
        Question("travel_history", "Have you traveled abroad before?", ["Yes, many times", "Yes, 1-2 times", "No"]),
        Question("previous_visas", "Have you received visas before?", ["Yes, several times", "Yes, once", "No"]),
        Question("refusals", "Have you had visa refusals before?", ["No", "Yes, once", "Yes, several times"]),
        Question("purpose", "Is your travel purpose clear?", ["Yes, very clear", "Partly", "Not really"]),
        Question("documents", "How ready are your documents?", ["Almost all ready", "Partly ready", "Not ready yet"]),
        Question("time_to_apply", "When do you plan to apply?", ["This week", "This month", "Within 1-3 months", "Not decided yet"]),
    ],
}


SPECIFIC = {
    "usa": {
        "hy": [
            Question("usa_ds160", "Լրացրե՞լ եք DS-160 ձևաթուղթը։", ["Այո", "Ոչ", "Չգիտեմ ինչ է դա"]),
            Question("usa_interview", "Պատրա՞ստ եք ԱՄՆ դեսպանատան հարցազրույցին։", ["Այո", "Մասամբ", "Ոչ"]),
            Question("usa_214b", "Եթե նախկինում ԱՄՆ մերժում է եղել, պատճառը 214(b)՞ էր։", ["Մերժում չեմ ունեցել", "Այո", "Չգիտեմ"]),
            Question("usa_ties", "Կարո՞ղ եք ապացուցել, որ կվերադառնաք ձեր բնակության երկիր։", ["Այո, ուժեղ ապացույցներ ունեմ", "Մասամբ", "Դժվար կլինի"]),
        ],
        "ru": [
            Question("usa_ds160", "Вы уже заполняли форму DS-160?", ["Да", "Нет", "Не знаю, что это"]),
            Question("usa_interview", "Готовы к интервью в посольстве США?", ["Да", "Частично", "Нет"]),
            Question("usa_214b", "Если был отказ США, причина была 214(b)?", ["Отказа не было", "Да", "Не знаю"]),
            Question("usa_ties", "Можете доказать, что вернетесь в страну проживания?", ["Да, есть сильные доказательства", "Частично", "Будет сложно"]),
        ],
        "en": [
            Question("usa_ds160", "Have you completed the DS-160 form?", ["Yes", "No", "I do not know what it is"]),
            Question("usa_interview", "Are you ready for the US embassy interview?", ["Yes", "Partly", "No"]),
            Question("usa_214b", "If you had a US refusal, was it under 214(b)?", ["No refusal", "Yes", "I do not know"]),
            Question("usa_ties", "Can you prove you will return to your country of residence?", ["Yes, strong proof", "Partly", "It may be difficult"]),
        ],
    },
    "germany": {
        "hy": [
            Question("de_purpose_doc", "Ունե՞ք Գերմանիայի համար հիմնական փաստաթուղթ՝ ընդունելություն, պայմանագիր կամ հրավեր։", ["Այո", "Գործընթացի մեջ է", "Ոչ"]),
            Question("de_finance", "Ունե՞ք blocked account, sponsor կամ բավարար ֆինանսական ապացույց։", ["Այո", "Մասամբ", "Ոչ"]),
            Question("de_accommodation", "Ունե՞ք բնակության հասցե / կացության ապացույց Գերմանիայում։", ["Այո", "Մասամբ", "Ոչ"]),
            Question("de_insurance", "Ունե՞ք առողջության / ճանապարհորդական ապահովագրություն։", ["Այո", "Կպատրաստեմ", "Ոչ"]),
        ],
        "ru": [
            Question("de_purpose_doc", "Есть основной документ для Германии: поступление, контракт или приглашение?", ["Да", "В процессе", "Нет"]),
            Question("de_finance", "Есть blocked account, спонсор или достаточное финансовое подтверждение?", ["Да", "Частично", "Нет"]),
            Question("de_accommodation", "Есть адрес проживания / подтверждение жилья в Германии?", ["Да", "Частично", "Нет"]),
            Question("de_insurance", "Есть медицинская / travel страховка?", ["Да", "Подготовлю", "Нет"]),
        ],
        "en": [
            Question("de_purpose_doc", "Do you have the main Germany document: admission, contract or invitation?", ["Yes", "In process", "No"]),
            Question("de_finance", "Do you have a blocked account, sponsor or sufficient financial proof?", ["Yes", "Partly", "No"]),
            Question("de_accommodation", "Do you have accommodation proof in Germany?", ["Yes", "Partly", "No"]),
            Question("de_insurance", "Do you have health / travel insurance?", ["Yes", "Will prepare", "No"]),
        ],
    },
    "france": {},
    "schengen": {},
    "uk": {
        "hy": [Question("uk_documents", "Ունե՞ք Մեծ Բրիտանիայի համար այցի նպատակի ապացույցներ։", ["Այո", "Մասամբ", "Ոչ"])],
        "ru": [Question("uk_documents", "Есть финансовые документы и доказательство цели поездки в Великобританию?", ["Да", "Частично", "Нет"])],
        "en": [Question("uk_documents", "Do you have financial documents and proof of UK travel purpose?", ["Yes", "Partly", "No"])],
    },
    "canada": {
        "hy": [Question("ca_ties", "Կանադայի համար կարո՞ղ եք ցույց տալ կապեր ձեր երկրի հետ։", ["Այո", "Մասամբ", "Ոչ"])],
        "ru": [Question("ca_ties", "Для Канады можете показать сильные связи со своей страной?", ["Да", "Частично", "Нет"])],
        "en": [Question("ca_ties", "For Canada, can you show strong ties to your country?", ["Yes", "Partly", "No"])],
    }
}

SCHENGEN_Q = {
    "hy": [
        Question("sch_itinerary", "Ունե՞ք հստակ ճամփորդական պլան։", ["Այո", "Մասամբ", "Ոչ"]),
        Question("sch_booking", "Ունե՞ք հյուրանոցի ամրագրում կամ հրավեր։", ["Այո", "Մասամբ", "Ոչ"]),
        Question("sch_insurance", "Ունե՞ք ճանապարհորդական ապահովագրություն։", ["Այո", "Կպատրաստեմ", "Ոչ"]),
        Question("sch_return", "Կարո՞ղ եք ապացուցել վերադարձի մտադրությունը։", ["Այո", "Մասամբ", "Դժվար կլինի"]),
    ],
    "ru": [
        Question("sch_itinerary", "Есть четкий план поездки?", ["Да", "Частично", "Нет"]),
        Question("sch_booking", "Есть бронь отеля или приглашение?", ["Да", "Частично", "Нет"]),
        Question("sch_insurance", "Есть travel insurance?", ["Да", "Подготовлю", "Нет"]),
        Question("sch_return", "Можете доказать намерение вернуться?", ["Да", "Частично", "Будет сложно"]),
    ],
    "en": [
        Question("sch_itinerary", "Do you have a clear travel itinerary?", ["Yes", "Partly", "No"]),
        Question("sch_booking", "Do you have hotel booking or invitation?", ["Yes", "Partly", "No"]),
        Question("sch_insurance", "Do you have travel insurance?", ["Yes", "Will prepare", "No"]),
        Question("sch_return", "Can you prove your intention to return?", ["Yes", "Partly", "It may be difficult"]),
    ],
}
SPECIFIC["france"] = SCHENGEN_Q
SPECIFIC["schengen"] = SCHENGEN_Q


def get_questions(lang: str, country: str) -> list[Question]:
    country_key = normalize_country(country)
    return COMMON[lang] + SPECIFIC.get(country_key, {}).get(lang, [])
