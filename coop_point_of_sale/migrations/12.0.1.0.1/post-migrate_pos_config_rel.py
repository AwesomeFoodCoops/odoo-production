def migrate(cr, version):
    if not version:
        return
    cr.execute("""alter table rel_pos_config_journal
                    DROP CONSTRAINT
                    rel_pos_config_journal_rel_account_journal_pos_fkey;
                """
               )
    cr.execute("""alter table rel_pos_config_journal
                    ADD CONSTRAINT
                    rel_pos_config_journal_rel_account_journal_pos_fkey
                    FOREIGN KEY (rel_account_journal_pos)
                    REFERENCES public.pos_config (id) MATCH SIMPLE
                    ON UPDATE NO ACTION
                    ON DELETE CASCADE;
                """
               )
