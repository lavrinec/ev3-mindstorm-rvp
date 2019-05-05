function T = read(path, fileName)
    path = fullfile(path,strcat('\', fileName,'.txt'));
    fileID = fopen(path,'r');
    formatSpec = '%d %f';
    size = [2 Inf];

    %normaliziraj cas
    T = fscanf(fileID,formatSpec,size)';
    startTime = T(1,2);
    T(:,2) = T(:,2) - startTime;
    
    fclose(fileID);
end