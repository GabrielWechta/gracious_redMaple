# gracious_redMaple

Repository for the compiler designed and wrote for JFTT - lecture on Wrocław University of Science and Technology.

## Description

Ok, so you may ask yourself: <b>What? Is this a compiler? Like gcc, or g++?</b>  
Yes, it is, simpler but yeah.  
There is no point in discussing how though it is to make it. I cried, I laughed, no regrets.  
To be honest. This project is amazing. I don't mean my code especially, but the idea - to make one semester lecture
about programming languages that ends in writing your own compiler, is there anything more WPPT?  
I remember how on different occasions older students were saying not pretty stuff about writing compiler and well, now I
am older student, I guess.  
Nevertheless, now it is done.

This is grammar for language:

    program      -> DECLARE declarations BEGIN commands END
                | BEGIN commands END
                
    declarations -> declarations pidentifier;
                | declarations pidentifier(num:num);
                | pidentifier
                | pidentifier(num:num)

    commands     -> commands command
                | command

    command      -> identifier := expression;
                | IF condition THEN commands ELSE commands ENDIF
                | IF condition THEN commands ENDIF
                | WHILE condition DO commands ENDWHILE
                | REPEAT commands UNTIL condition;
                | FOR pidentifier FROM value TO value DO commands ENDFOR
                | FOR pidentifier FROM value DOWNTO value DO commands ENDFOR
                | READ identifier;
                | WRITE value;

    expression   -> value
                | value + value
                | value - value
                | value * value
                | value / value
                | value % value

    condition    -> value = value
                | value != value
                | value < value
                | value > value
                | value <= value
                | value >= value

    value        -> num
                | identifier
 
    identifier   -> pidentifier
                | pidentifier(pidentifier)
                | pidentifier(num)

This is example program, it prints prime factor decomposition for given number:

    [ Rozklad liczby na czynniki pierwsze ]
    DECLARE
        n; m; reszta; potega; dzielnik;
    IN
        READ n;
        dzielnik := 2;
        m := dzielnik * dzielnik;
        WHILE n >= m DO
            potega := 0;
            reszta := n % dzielnik;
            WHILE reszta = 0 DO
                n := n / dzielnik;
                potega := potega + 1;
                reszta := n % dzielnik;
            ENDWHILE
            IF potega > 0 THEN [ czy znaleziono dzielnik ]
                WRITE dzielnik;
                WRITE potega;
            ELSE
                dzielnik := dzielnik + 1;
                m := dzielnik * dzielnik;
            ENDIF
        ENDWHILE
        IF n != 1 THEN [ ostatni dzielnik ]
            WRITE n;
            WRITE 1;
        ENDIF
    END

There is also virtual machine designed and wrote by PhD Maciej Gębala, it's in a folder 'maszyna_wirtualna'.

## Technologies

I used Ply (https://www.dabeaz.com/ply/) which is basically python implementation of, I am more than sure wellknown to
everybody, yacc and bison - parsing tools.  
I used `Ply 3.11`, which is the latest release, when I am writing this. Also, this program was written in `Python 3.8`.

| Instruction        | Interpretation           | Time Cost  |
| ------------- |:-------------:| -----:|
|GET x |pobraną liczbę zapisuje w komórce pamięci prx oraz k ← k + 1 |100
|PUT x |wyświetla zawartość komórki pamięci prx oraz k ← k + 1 |100
|LOAD x y |r_x ← p_r_y oraz k ← k + 1 |20
|STORE x y |p_r_y ← r_x oraz k ← k + 1 |20
|ADD x y |r_x ← r_x + r_y oraz k ← k + 1 |5
|SUB x y |r_x ← max{r_x − r_y, 0} oraz k ← k + 1 |5
|RESET x |r_x ← 0 oraz k ← k + 1 |1
|INC x |r_x ← r_x + 1 oraz k ← k + 1 |1
|DEC x |r_x ← max(r_x − 1, 0) oraz k ← k + 1 |1
|SHR x |r_x ← r_x/2 oraz k ← k + 1 |1
|SHL x |r_x ← r_x ∗ 2 oraz k ← k + 1 |1
|JUMP j |k ← k + j |1
|JZERO x j |jeśli r_x = 0 to k ← k + j, w p.p. k ← k + 1 |1
|JODD x j |jeśli r_x nieparzyste to k ← k + j, w p.p. k ← k + 1 |1
|HALT |zatrzymaj program |0

## Studencie
Bardzo mi przykro, że tu wylądowałeś.  
Ale dasz radę, serio. Tylko kup sobie kilo kawy.  
Moja implementacja w kategoriach wyniku na ocenianiu jest słaba. Między innymi dlatego, że:
1. **\-** wszystkie stałe są zapisywane do pamięci, a nie ma takiej potrzeby, natomiast wtedy procedura wczytania do rejestrów wartości jest niezależna od typu, co znacznie ułatwia wygląd funckji wczytującej.
2. **\-** wszystkie rejestry są wpisane z palca (XD), jako że na przykład w takim dzieleniu niezbędne jest 5 (chyba) rejestrów, a do operacji, w pierwszym miejscu, wczytania dzielnika i dzielnej do rejestrów potrzebne są 2, a razem mamy tylko 6, to aby uniknąć niespodziewanych błedóœ postanowiłem na sztywno je ustawiać co jest skrajnie nieoptymalne, ale spokój jest najcenniejszy.  
---

Natomiast jeśli kończy ci się czas, żona ma termin za tydzień, albo nie masz pojęcia co zrobić i ogarnia cię panika, to są też zalety:
3. **+** jest fantastyczny i prosty w użytkowaniu generator drzewa wyprowadzenia. Jest wpaniały bo od razu zamienia FOR'y na JUMP'y i wstawia labele, które następnie łatwo jest ponadpisywać aby odzyskać z nich adres względnego skoku.
4. **+** jest porządny symbol table, który w miarę rozsądnie sprawdza błędy.
5. **+** błędnego użycia iteratora wewnątrz pętli nie można wykryć (u mnie) robiąc jeden przebieg. Na szczęście są dozwolone multi-przebiegi. Co jest realizowane łatwo w parserze.

Jeżeli zależy ci na ocenie, to spójrz jak robią to prosi:
* https://github.com/quetzelcoatlus/PWr/tree/master/Semestr_5/Jezyki_Formalne_i_Techniki_Translacji_JFTT/Lista_4
* https://github.com/chceswieta?tab=repositories