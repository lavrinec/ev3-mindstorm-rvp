path = 'C:\Users\Ivan\Documents\FRI\Magisterij\1.Letnik\RVP\vaje\analiza';

T1 = read(path, 'meritve0');
%koti so negativni, popravi naslednjic pri izpisu
T1(:,1) = T1(:,1)*-1;

T2 = read(path, 'meritve01');
%koti so negativni, popravi naslednjic pri izpisu
T2(:,1) = T2(:,1)*-1;

T3 = readE(path, 'meritveC01');
T4 = readE(path, 'meritveC0');

figure(1); 
hold on;
plot(T1(:,2), T1(:,1), 'r')
hold on;
plot(T2(:,2), T2(:,1), 'b')

hold on;
plot(T3(:,3), T3(:,1))
hold on;
plot(T4(:,3), T4(:,1))

hold off;
legend('I=0','I=0.1', 'counter, I=0', 'counter, I=0.1')

