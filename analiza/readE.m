function T = readE(path, fileName)
    path = fullfile(path,strcat('\', fileName,'.txt'));
    fileID = fopen(path,'r');
    formatSpec = '%d %f %f';
    size = [3 Inf];

    %normaliziraj cas
    T = fscanf(fileID,formatSpec,size)';
    startTime = T(1,3);
    T(:,3) = T(:,3) - startTime;
    
    fclose(fileID);
end