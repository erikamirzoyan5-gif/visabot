from dataclasses import dataclass
from questions import normalize_country


@dataclass
class ScoreResult:
    score: int
    strengths: list[str]
    risks: list[str]
    recommendations: list[str]


def answer_has(answer: str, words: list[str]) -> bool:
    value = answer.lower()
    return any(w.lower() in value for w in words)


def calculate_score(data: dict) -> ScoreResult:
    answers: dict[str, str] = data.get("answers", {})
    country = data.get("country", "")
    country_key = normalize_country(country)

    score = 50
    strengths: list[str] = []
    risks: list[str] = []
    recommendations: list[str] = []

    def add(points: int, strength: str | None = None, risk: str | None = None, rec: str | None = None) -> None:
        nonlocal score
        score += points
        if strength:
            strengths.append(strength)
        if risk:
            risks.append(risk)
        if rec:
            recommendations.append(rec)

    # Passport
    passport = answers.get("passport", "")
    if answer_has(passport, ["больше 1", "more than", "1 տարուց"]):
        add(8, "Անձնագրի վավերականության ժամկետը բավարար է։")
    elif answer_has(passport, ["скоро", "expires", "շուտով"]):
        add(-4, risk="Անձնագրի վավերականության ժամկետը կարող է կարճ լինել։", rec="Մինչ դիմելը ստուգեք անձնագրի վավերականության ժամկետը։")
    elif passport:
        add(-18, risk="Գործող անձնագիր չկա։", rec="Առաջին հերթին անհրաժեշտ է պատրաստել կամ թարմացնել անձնագիրը։")

    # Employment / income
    employment = answers.get("employment", "")
    if answer_has(employment, ["официаль", "official", "պաշտոնական", "business", "бизнес", "բիզնես"]):
        add(12, "Աշխատանքի կամ բիզնեսի առկայությունը դրական գործոն է։")
    elif answer_has(employment, ["student", "студент", "ուսանող"]):
        add(3, "Ուսանողի կարգավիճակը կարող է ընդունելի լինել ճիշտ փաստաթղթերի դեպքում։", rec="Պատրաստեք ուսանողական տեղեկանք և անհրաժեշտության դեպքում հովանավորի փաստաթղթեր։")
    elif employment:
        add(-12, risk="Չկա կայուն աշխատանք կամ բիզնես։", rec="Ամրապնդեք ֆինանսական ապացույցները և կապերը բնակության երկրի հետ։")

    experience = answers.get("experience", "")
    if answer_has(experience, ["более 3", "more than 3", "3 տարուց"]):
        add(8, "Երկարատև աշխատանքային կամ բիզնես փորձը դրական գործոն է։")
    elif answer_has(experience, ["до 6", "less than", "մինչև 6"]):
        add(-4, risk="Աշխատանքային կամ բիզնես փորձը դեռ կարճ է։")

    income = answers.get("income", "")
    if answer_has(income, ["более $2000", "more than $2000", "$2000-ից"]):
        add(12, "Եկամտի մակարդակը ուժեղ է։")
    elif answer_has(income, ["$1000-$2000"]):
        add(8, "Եկամտի մակարդակը ընդունելի է։")
    elif answer_has(income, ["нет стабиль", "no stable", "կայուն եկամուտ չունեմ"]):
        add(
            -18,
            risk="Կայուն եկամուտ չկա։",
            rec="Պատրաստեք հովանավորի փաստաթղթեր կամ ավելի ուժեղ ֆինանսական ապացույցներ։"
        )
    elif income:
        add(-4, risk="Եկամուտը կարող է ցածր լինել ընտրված վիզայի համար։")

    taxes = answers.get("taxes", "")
    if answer_has(taxes, ["полностью", "fully", "լիարժեք"]):
        add(8, "Եկամուտը հնարավոր է ապացուցել փաստաթղթերով։")
    elif answer_has(taxes, ["нет", "no", "ոչ"]):
        add(
            -8,
            risk="Եկամուտը դժվար է ապացուցել փաստաթղթերով։",
            rec="Պատրաստեք պաշտոնական եկամուտը հաստատող փաստաթղթեր։"
        )

    bank = answers.get("bank_statement", "")
    if answer_has(bank, ["хорош", "good", "բավարար"]):
        add(12, "Բանկային քաղվածքը դրական է գնահատվում։")
    elif answer_has(bank, ["небольш", "low", "քիչ"]):
        add(
            2,
            risk="Բանկային մնացորդը կարող է ցածր լինել։",
            rec="Մինչ դիմելը ցանկալի է բարելավել բանկային մնացորդը։"
        )
    elif bank:
        add(
            -15,
            risk="Բանկային քաղվածք չկա։",
            rec="Պատրաստեք բանկային քաղվածք։"
        )

    amount = answers.get("bank_amount", "")
    if answer_has(amount, ["более $7000", "more than $7000", "$7000-ից"]):
        add(12, "Բանկային մնացորդը ուժեղ է։")
    elif answer_has(amount, ["$3000-$7000"]):
        add(8, "Բանկային մնացորդը ընդունելի է։")
    elif answer_has(amount, ["до $1000", "under $1000", "մինչև $1000", "нет", "none", "չունեմ"]):
        add(-10, risk="Բանկային մնացորդը կարող է բավարար չլինել։")

    # Ties
    prop = answers.get("property", "")
    if answer_has(prop, ["несколько", "several", "մի քանի"]):
        add(10, "Բնակության երկրի հետ կապերը ուժեղ են։")
    elif answer_has(prop, ["квартира", "apartment", "բնակարան", "семья", "family", "ընտանիք", "business", "машина", "մեքենա"]):
        add(6, "Կան կապեր բնակության երկրի հետ։")
    elif prop:
        add(
            -8,
            risk="Բնակության երկրի հետ կապերը թույլ են։",
            rec="Պատրաստեք փաստաթղթեր, որոնք ապացուցում են ձեր կապերը բնակության երկրի հետ։"
        )

    travel = answers.get("travel_history", "")
    if answer_has(travel, ["много", "many", "շատ"]):
        add(9, "Ճամփորդական պատմությունը դրական է։")
    elif answer_has(travel, ["1-2"]):
        add(4, "Կա որոշակի ճամփորդական պատմություն։")
    elif travel:
        add(-5, risk="Ճամփորդական պատմություն չկա։")

    visas = answers.get("previous_visas", "")
    if answer_has(visas, ["несколько", "several", "մի քանի"]):
        add(8, "Նախկինում վիզաներ ստանալու փորձը դրական գործոն է։")
    elif answer_has(visas, ["1 раз", "once", "1 անգամ"]):
        add(4, "Նախկինում վիզա ստանալու փորձ կա։")

    refusals = answers.get("refusals", "")
    if answer_has(refusals, ["нет", "no", "ոչ"]):
        add(8, "Նախկինում վիզայի մերժում չի եղել։")
    elif answer_has(refusals, ["несколько", "several", "մի քանի"]):
        add(
            -20,
            risk="Նախկինում եղել են մի քանի վիզայի մերժումներ։",
            rec="Մինչ նոր դիմումը պետք է վերլուծել մերժման պատճառները։"
        )
    elif refusals:
        add(
            -12,
            risk="Նախկինում եղել է վիզայի մերժում։",
            rec="Պատրաստեք ավելի ուժեղ փաստաթղթեր և հստակ բացատրություն։"
        )

    purpose = answers.get("purpose", "")
    if answer_has(purpose, ["очень", "very", "շատ"]):
        add(8, "Ուղևորության նպատակը հստակ է։")
    elif answer_has(purpose, ["не очень", "not really", "ոչ այնքան"]):
        add(
            -8,
            risk="Ուղևորության նպատակը բավականաչափ հստակ չէ։",
            rec="Պատրաստեք հստակ բացատրություն և նպատակը հաստատող փաստաթղթեր։"
        )

    docs = answers.get("documents", "")
    if answer_has(docs, ["почти", "almost", "գրեթե"]):
        add(8, "Փաստաթղթերը գրեթե պատրաստ են։")
    elif answer_has(docs, ["не готовы", "not ready", "պատրաստ չեն"]):
        add(
            -10,
            risk="Փաստաթղթերը դեռ պատրաստ չեն։",
            rec="Մինչ դիմելը պատրաստեք ամբողջական փաստաթղթերի փաթեթ։"
        )

    # Country-specific
    if country_key == "usa":
        if answer_has(answers.get("usa_interview", ""), ["нет", "no", "ոչ"]):
            add(
                -10,
                risk="ԱՄՆ դեսպանատան հարցազրույցի պատրաստվածությունը թույլ է։",
                rec="Պետք է նախապես պատրաստվել ԱՄՆ վիզայի հարցազրույցին։"
            )
        if answer_has(answers.get("usa_ties", ""), ["сложно", "difficult", "դժվար"]):
            add(
                -15,
                risk="ԱՄՆ-ի համար վերադարձի մտադրության ապացույցները թույլ են։",
                rec="Ուժեղացրեք բնակության երկրի հետ կապերը և վերադարձի ապացույցները։"
            )
        recommendations.append(
            "ԱՄՆ վիզայի դեպքում կարևոր է կենտրոնանալ DS-160 ձևաթղթի ճշգրտության, հարցազրույցի պատրաստվածության, ֆինանսական կայունության, բնակության երկրի հետ կապերի և ուղևորության հստակ նպատակի վրա։"
        )

    elif country_key == "germany":
        if answer_has(answers.get("de_purpose_doc", ""), ["нет", "no", "ոչ"]):
            add(
                -14,
                risk="Գերմանիայի համար հիմնական փաստաթուղթը բացակայում է։",
                rec="Պատրաստեք ընդունելության նամակ, աշխատանքային պայմանագիր կամ հրավեր։"
            )
        if answer_has(answers.get("de_finance", ""), ["нет", "no", "ոչ"]):
            add(
                -14,
                risk="Գերմանիայի համար ֆինանսական ապացույցները թույլ են։",
                rec="Պատրաստեք blocked account, հովանավորի փաստաթղթեր կամ բավարար ֆինանսական միջոցների ապացույց։"
            )
        recommendations.append(
            "Գերմանիայի համար կարևոր է կենտրոնանալ ֆինանսական ապացույցների, բնակության հասցեի, ապահովագրության և ուղևորության նպատակին համապատասխան փաստաթղթերի վրա։"
        )

    elif country_key in {"france", "schengen"}:
        if answer_has(answers.get("sch_booking", ""), ["нет", "no", "ոչ"]):
            add(
                -8,
                risk="Հյուրանոցի ամրագրում կամ հրավեր չկա։",
                rec="Պատրաստեք հյուրանոցի ամրագրում կամ հրավեր։"
            )
        if answer_has(answers.get("sch_insurance", ""), ["нет", "no", "ոչ"]):
            add(
                -8,
                risk="Ճանապարհորդական ապահովագրություն չկա։",
                rec="Պատրաստեք գործող Շենգեն ճանապարհորդական ապահովագրություն։"
            )
        recommendations.append(
            "Շենգեն վիզայի համար պատրաստեք ճամփորդական պլան, ամրագրումներ, ապահովագրություն, բանկային քաղվածք և վերադարձի երաշխիքներ։"
        )

    elif country_key == "uk":
        recommendations.append(
            "Մեծ Բրիտանիայի վիզայի համար կարևոր են ֆինանսական փաստաթղթերը, աշխատանքի ապացույցը, ուղևորության նպատակը և վերադարձի ուժեղ ապացույցները։"
        )

    elif country_key == "canada":
        recommendations.append(
            "Կանադայի վիզայի համար կարևոր են ֆինանսական կարողությունը, բնակության երկրի հետ կապերը, աշխատանքի կամ ուսման ապացույցը և ուղևորության հստակ նպատակը։"
        )

    else:
        recommendations.append(
            "Պատրաստեք ամբողջական փաստաթղթերի փաթեթ, ֆինանսական ապացույցներ և ուղևորության հստակ նպատակ։"
        )

    score = max(5, min(95, score))

    if not strengths:
        strengths.append("Փաստաթղթերի ուսումնասիրությունից հետո կարող են հայտնաբերվել դրական գործոններ։")
    if not risks:
        risks.append("Ձեր պատասխանների հիման վրա մեծ ռիսկ չի հայտնաբերվել։")
    if not recommendations:
        recommendations.append("Մինչ դիմելը խորհուրդ է տրվում անցնել խորհրդատվություն և ստուգել փաստաթղթերը։")

    return ScoreResult(
        score=score,
        strengths=dedupe(strengths)[:6],
        risks=dedupe(risks)[:6],
        recommendations=dedupe(recommendations)[:6],
    )


def dedupe(items: list[str]) -> list[str]:
    result = []
    seen = set()
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result
