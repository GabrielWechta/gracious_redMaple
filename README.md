# gracious_redMaple
Repository for compiler designed and wrote for JFTT - lecture on Wrocław University of Science and Technology.
## Description
Ok, so you may ask yourself: <b>What? Is this compiler? Like gcc, or g++?</b>  
Yes, it is, simpler but yeah.  
There is no point in discussing how thougth it is to make it. I cried, I laughed and now I have gray hair.  
But to be honest. This project is amazing. And I don't mean my code especially but the idea - to make one semeseter lecture about programming languages that ends in writting your own compiler, is there anything more WPPT? I remember how on diffrent occasions older students were saying not pretty stuff about writing compiler and well they were close from truth. But now it is done.
I can't wait to imagine those faces:  
A: - I wrote app for Android on my studies.  
B: - I wrote REST web app.  
Me: \*waving my hand\*


This is grammar for languange:

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
There is also virtual machine designed and wrote by PhD Maciej Gębala, it's in folder 'maszyna_wirtualna'.

## Technologies 
