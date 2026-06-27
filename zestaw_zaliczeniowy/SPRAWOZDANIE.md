# Sprawozdanie — zestaw zaliczeniowy AAP

**Autor:** Michał Surzyn · **Dataset:** `stanfordnlp/imdb` · **Notebook:** `AAP_Zestaw_Zaliczeniowy.ipynb`

Notebook jest uruchamialny od góry do dołu po `python preflight_download.py`. Poniżej skrót rozwiązań i wniosków.

## Lab 1 — dekoratory

`@retry` ponawia wywołanie do `max_attempts` razy z czasem snu `delay * backoff**próba` i podnosi ostatni wyjątek po wyczerpaniu prób. `@cache_to_disk` liczy klucz `md5(repr(args, kwargs))`, a wynik trzyma w pliku JSON — drugie wywołanie z tymi samymi argumentami nie wykonuje ciała funkcji. Na `flaky_fetch` (50% awaryjności) przy 5 próbach sukces wypada w ~96–97% na 100 wywołaniach, zgodnie z teorią `1 − 0.5⁵ = 0.969`.

## Lab 2 — współbieżność

`sentiment_score` to leksykonowy licznik (pozytywne − negatywne) na tokenach `\w+`. Porównanie na 5000 recenzji: wersja sekwencyjna i ThreadPool dają zbliżony czas (zadanie jest CPU-bound, więc GIL blokuje przyspieszenie wątków), a `multiprocessing.Pool` z `chunksize=100` wygrywa, bo procesy omijają GIL. Wyniki wszystkich trzech wariantów są identyczne.

## Lab 3 — testowanie

`Tokenizer` (strip HTML → lowercase → `re.findall(r"\w+", flags=re.UNICODE)` → filtr długości) przechodzi cały zestaw pytest: parametryzacja (pusty string, sam HTML, mieszany case, interpunkcja, polskie diakrytyki, zwykłe zdanie), fixtury `tokenizer` i `imdb_sample` oraz `xfail` dla niewspieranego `user@domain.com`. Słownik na 100 recenzjach to rząd kilku tysięcy unikalnych tokenów (prawo Heapsa — wzrost subliniowy).

## Lab 4 — bazy danych

Schemat dokumentowy `reviews_json(id, doc)` z `json_extract` odpowiada na te same pytania co schemat relacyjny. JSON jest większy (powtarzane klucze) i wolniejszy w agregacji (parsowanie per wiersz, brak indeksu na polach). Dla stałego schematu i zapytań analitycznych lepszy jest klasyczny SQL kolumnowy; JSON opłaca się przy zmiennej strukturze dokumentów.

## Lab 5 — PySpark

Window functions: `row_number()` po `partitionBy("label").orderBy(word_count desc)` daje ranking i top 3 per klasa, `avg().over(partitionBy("label"))` — różnicę od średniej klasowej, a `rowsBetween(-49, 0)` — średnią kroczącą po `id`. Tego nie da się zrobić zwykłym `groupBy`, bo agregacja redukuje wiersze, a tu każdy wiersz ma zostać z dodatkową kolumną. Wykres pokazuje zbliżony rozkład długości w obu klasach.

## Lab 6 — data quality

`DataContract` zbiera nazwane reguły z wagą (`info`/`warning`/`error`), `DataValidator` zwraca raport `{reguła: {passed, severity, details}}` i rzuca wyjątek przy niespełnionej regule `error` (fail-fast). Kontrakt dla IMDB ma 7 reguł; `no_html_tags` (warning) pada i jest odnotowana w raporcie `data_quality_report.json`, ale nie blokuje walidacji. Osobne demo pokazuje fail-fast na celowo zepsutych danych. Różnica audyt/kontrakt: kontrakt to warunek wejścia (blokuje złe dane), audyt to opis stanu danych w czasie.
