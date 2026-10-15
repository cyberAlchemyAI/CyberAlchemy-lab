"""Emit three explicit uses of the independent grammar's mutual recursors."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
MINORS='''
    (primitive_complete _ .null (.literal _ .null .null))
    (primitive_complete _ (.boolean false) (.literal _ (.boolean false) .false))
    (primitive_complete _ (.boolean true) (.literal _ (.boolean true) .true))
    (fun token grammar => primitive_complete _ (.number token) (.number token grammar))
    (fun word units meaning => primitive_complete word (.string units) (.string word units meaning))
    (fun space ws => empty_array_complete space ws)
    (fun left text right values wl _ wr ih => array_complete left text right values wl wr ih)
    (fun space ws => empty_object_complete space ws)
    (fun left text right entries wl _ wr ih => object_complete left text right entries wl wr ih)
    (fun text value meaning ih => items_one_complete text value meaning ih)
    (fun text left right remaining value values head wl wr _ ihHead ihTail =>
      items_cons_complete text left right remaining value values head wl wr ihHead ihTail)
    (fun key left right text units value name wl wr meaning ih =>
      members_one_complete key left right text units value name wl wr meaning ih)
    (fun key left right text before after remaining units value entries name wl wr meaning wb wa _ ihHead ihTail =>
      members_cons_complete key left right text before after remaining units value entries name wl wr meaning wb wa ihHead ihTail)
    meaning
'''
def run():
    source='import CompletenessInterfaces\nset_option autoImplicit false\nnamespace RelationalSuccessor.CandidateJsonCompleteness\nopen CandidateJsonBytes CandidateJsonTokens CandidateJsonParser\n'
    names=[]
    for name,family,carrier,output in [('grammar_value_complete','ValueMeaning','RawValue','ValueComplete'),('grammar_items_complete','ItemsMeaning','List RawValue','ItemsComplete'),('grammar_members_complete','MembersMeaning','List (List Nat × RawValue)','MembersComplete')]:
        names.append(name)
        source+=f'\ntheorem {name} (word : List Nat) (value : {carrier}) (meaning : {family} word value) : {output} word value := by\n'
        source+=f'  exact {family}.rec\n    (motive_1 := fun word value _ => ValueComplete word value)\n    (motive_2 := fun word values _ => ItemsComplete word values)\n    (motive_3 := fun word entries _ => MembersComplete word entries)'+MINORS
    source+='\n'+'\n'.join('#print axioms '+name for name in names)+'\nend RelationalSuccessor.CandidateJsonCompleteness\n'
    (HERE/'RecursiveCompleteness.lean').write_text(source)
if __name__=='__main__':run()
