BEGIN TRANSACTION;

CREATE DOMAIN String1 AS varchar CHECK(value ~ '^\S$|^\S.*\S$');
CREATE DOMAIN SlurmJobId AS integer CHECK(value >= 1);

CREATE TABLE IF NOT EXISTS Blackbox (
    name String1 NOT NULL,
    PRIMARY KEY (name)
);

CREATE TABLE IF NOT EXISTS Job (
    job_id SlurmJobId NOT NULL,
    blackbox String1 NOT NULL,
    submit_time timestamp NOT NULL DEFAULT NOW(),
    start_time timestamp NULL,
    end_time timestamp NULL,
    result real NULL,
    PRIMARY KEY (job_id),
    FOREIGN KEY (blackbox) REFERENCES Blackbox (name) ON DELETE CASCADE,
    CHECK ( 
        -- C.Job.continuity_1
        (start_time IS NULL OR submit_time <= start_time) AND

        -- C.Job.continuity_2
        (end_time IS NULL OR start_time <= end_time) AND

        -- C.Job.end_implies_job_was_scheduled
        (end_time IS NULL OR start_time IS NOT NULL) AND

        -- C.Job.result_only_on_end_time
        -- C.Job.end_time_only_on_result
        (
            (end_time IS NULL AND result IS NULL) OR
            (end_time IS NOT NULL AND result IS NOT NULL)
        )
    )
);

CREATE TABLE IF NOT EXISTS Parameter (
    key String1 NOT NULL,
    blackbox String1 NOT NULL,
    PRIMARY KEY (key, blackbox),
    FOREIGN KEY (blackbox) REFERENCES Blackbox (name) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ParameterInstance (
    id serial NOT NULL,
    value real NOT NULL,
    parameter_key String1 NOT NULL,
    blackbox String1 NOT NULL,
    job_id SlurmJobId NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (parameter_key, blackbox) REFERENCES Parameter (key, blackbox) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES Job (job_id) ON DELETE CASCADE
);


REVOKE UPDATE (name) ON Blackbox FROM PUBLIC;

REVOKE UPDATE (job_id) ON Job FROM PUBLIC;
REVOKE DELETE ON Job FROM PUBLIC;

REVOKE UPDATE ON Parameter FROM PUBLIC;
REVOKE DELETE ON Parameter FROM PUBLIC;

REVOKE UPDATE ON ParameterInstance FROM PUBLIC;
REVOKE DELETE ON ParameterInstance FROM PUBLIC;

-- C.Job.all_parameters_are_instantiated
CREATE OR REPLACE FUNCTION C_Job_all_parameters_are_instantiated() RETURNS TRIGGER AS $C_Job_all_parameters_are_instantiated$
declare isError boolean := false; 
BEGIN 
    isError = EXISTS ( 
        SELECT *  
        FROM Parameter
        WHERE 
            NEW.blackbox = Parameter.blackbox AND
            NOT EXISTS (
                SELECT * 
                FROM ParameterInstance
                WHERE ParameterInstance.parameter_key = Parameter.key
            )
    ); 

    IF (isError) THEN raise EXCEPTION 'Constraint C_Job_all_parameters_are_instantiated violated'; 
    END IF; 

    RETURN NEW;
END; $C_Job_all_parameters_are_instantiated$ language plpgsql;

CREATE CONSTRAINT TRIGGER all_parameters_are_instantiated 
AFTER INSERT ON Job 
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE PROCEDURE C_Job_all_parameters_are_instantiated();

COMMIT;
