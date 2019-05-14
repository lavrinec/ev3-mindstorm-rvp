% path = 'drive50cm';
 path = 'rotate180';
fileName = '505000';
saveTo = fullfile(path,strcat('\', fileName,'.png'));
T1 = read(path, fileName);
%koti so negativni, popravi naslednjic pri izpisu
T1(:,1) = T1(:,1)*-1;

T2 = read(path, '005000');
%koti so negativni, popravi naslednjic pri izpisu
T2(:,1) = T2(:,1);

figure(1); 
hold on;
plot(T1(:,2), T1(:,1)*-1, 'r')
saveas(gcf,saveTo)
% hold on;
% plot(T2(:,2), T2(:,1), 'b')

% hold off;
% legend('I=0','I=0.1')

