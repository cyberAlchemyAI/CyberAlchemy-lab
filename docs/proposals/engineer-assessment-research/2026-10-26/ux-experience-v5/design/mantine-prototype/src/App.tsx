import { useState } from 'react';
import {
  Accordion, Alert, Badge, Button, Checkbox, Container, Divider, Group,
  Progress, Select, Stack, Stepper, Text, Title,
} from '@mantine/core';

const sessions = [
  ['01 / REASON', 'Unfamiliar problems', 'Explore possibilities, question assumptions and explain your reasoning.'],
  ['02 / DESIGN', 'Software architecture', 'Weigh product constraints, technical tradeoffs and likely failure modes.'],
  ['03 / COOPERATE', 'Working with others', 'Explain how a team could make decisions and share responsibility.'],
];

export function App() {
  const [step, setStep] = useState(0);
  const [research, setResearch] = useState(false);
  const [contact, setContact] = useState(false);
  const [mode, setMode] = useState<string | null>('Video answer');
  const advance = () => setStep((current) => Math.min(5, current + 1));

  return <>
    <header className="masthead"><Container size="lg" className="mastheadInner">
      <div className="wordmark"><span className="mark" aria-hidden="true" />Engineer Assessment</div>
      <Badge variant="light" color="gray" size="lg">Private pilot · prototype</Badge>
    </Container></header>
    <main>
      <Container size="lg" className="page">
        <div className="intro"><Text className="eyebrow">A challenge for software developers</Text>
          <Title order={1}>Think aloud.<br />Make it visible.</Title>
          <Text className="introText">Three short cases invite you to show how you reason. Feedback describes evidence in your answers; it is not a hiring decision.</Text>
          <Group gap="sm"><Badge variant="outline" color="assessment">3 cases</Badge><Badge variant="outline" color="assessment">10 recorded minutes each</Badge><Badge variant="outline" color="gray">Qualitative feedback</Badge></Group>
        </div>

        <nav aria-label="Challenge preview stages" className="journeyNav"><Stepper active={step} onStepClick={setStep} allowNextStepsSelect>
          <Stepper.Step label="Overview" /><Stepper.Step label="Choices" /><Stepper.Step label="Practice" />
          <Stepper.Step label="Case" /><Stepper.Step label="Feedback" /><Stepper.Step label="Data controls" />
        </Stepper></nav>

        {step === 0 && <section aria-labelledby="overview-title" className="experience"><div className="sectionHeading"><Text className="eyebrow">01 / The challenge</Text><Title order={2} id="overview-title">Three ways to reason.</Title><Text>Each session contains one reviewed case. The pilot studies whether these questions produce useful evidence; it does not assume three answers identify the best engineers.</Text></div>
          <div className="sessionList">{sessions.map(([number, title, detail]) => <div className="sessionRow" key={number}><Text className="sessionNumber">{number}</Text><Title order={3}>{title}</Title><Text>{detail}</Text></div>)}</div>
          <Alert color="assessment" variant="light" title="What you receive">Provisional, evidence-linked observations and a practice suggestion. No rank, percentile or employment verdict.</Alert>
        </section>}

        {step === 1 && <section aria-labelledby="choices-title" className="experience"><div className="sectionHeading"><Text className="eyebrow">02 / Purpose and control</Text><Title order={2} id="choices-title">Know what you are choosing.</Title><Text>The live service needs a reviewed notice and separate purpose decisions. The controls here only change this prototype screen.</Text></div>
          <div className="choiceRow"><div><Title order={3}>Challenge processing</Title><Text>Required to offer recording, transcript review and feedback under the approved service terms.</Text></div><Badge color="gray" variant="light">Required</Badge></div>
          <Checkbox className="choiceRow" label="Optional research use" description="Use eligible, pseudonymous evidence in the registered study." checked={research} onChange={(event) => setResearch(event.currentTarget.checked)} />
          <Checkbox className="choiceRow" label="Optional follow-up contact" description="Ask me later about my experience." checked={contact} onChange={(event) => setContact(event.currentTarget.checked)} />
          <Accordion variant="separated" className="plainAccordion"><Accordion.Item value="research"><Accordion.Control>What happens if I decline research?</Accordion.Control><Accordion.Panel>The offered challenge feedback remains available under its approved service purpose. Research extraction checks your current choice separately.</Accordion.Panel></Accordion.Item><Accordion.Item value="retention"><Accordion.Control>How long is my answer retained?</Accordion.Control><Accordion.Panel>The period is not approved yet. The live service must show the exact period and rights route before collection.</Accordion.Panel></Accordion.Item></Accordion>
        </section>}

        {step === 2 && <section aria-labelledby="practice-title" className="experience"><div className="sectionHeading"><Text className="eyebrow">03 / Device and access</Text><Title order={2} id="practice-title">Practice before the clock.</Title><Text>Choose an offered response path, check capture and try an unscored prompt. Access needs and technical failures do not become zero scores.</Text></div>
          <Select label="Response mode preview" description="Mode availability and equivalence require pilot review." data={['Video answer', 'Accessible alternative — staff route']} value={mode} onChange={setMode} maw={360} />
          <div className="practiceArea"><div className="cameraSymbol" aria-hidden="true">◌</div><Text fw={700}>Camera and microphone check appears here</Text><Text size="sm" c="dimmed">This prototype requests no device permission or media.</Text></div>
          <Alert color="yellow" variant="light" title="If recording is difficult">The live service must offer its approved alternate path or a support route before a scored case starts.</Alert>
        </section>}

        {step === 3 && <section aria-labelledby="case-title" className="experience"><div className="sectionHeading"><Text className="eyebrow">04 / Case workspace</Text><Title order={2} id="case-title">One case. A clear clock.</Title><Text>The case, assistance rule, recording state and camera preview stay together. Time and completion require server receipts in the live product.</Text></div>
          <div className="recordingStage"><div className="recordingTop"><Text fw={700}>SESSION 02 / SOFTWARE DESIGN</Text><Text className="clock">10:00</Text></div><div className="recordingBody"><div className="casePrompt"><Text className="eyebrow">Case preview · no recording</Text><Title order={3}>Design under a changing constraint.</Title><Text>Explain your assumptions, architecture choices, contention risks, latency and consistency tradeoffs.</Text><Text size="sm" mt="xl">The exact case and allowed help would appear here.</Text></div><div className="previewArea"><div className="cameraSymbol" aria-hidden="true">◌</div><Text fw={700}>Your camera preview</Text><Text size="sm">Blur state and capture health must be visible.</Text></div></div><div className="recordingBottom"><Text role="status">Ready to start · this prototype cannot record</Text><Button disabled variant="white">Start recording in the live service</Button></div></div>
          <Progress value={25} color="assessment" aria-label="Illustrative case journey progress" mt="xl" /><Text size="sm" c="dimmed" mt="xs">Ready → Record → Upload receipt → Transcript review</Text>
        </section>}

        {step === 4 && <section aria-labelledby="feedback-title" className="experience"><div className="sectionHeading"><Text className="eyebrow">05 / After review</Text><Title order={2} id="feedback-title">Feedback you can inspect.</Title><Text>Observations connect to exact evidence and a next practice step. Missing evidence is shown as missing.</Text></div>
          <div className="feedbackLayout"><div><Text className="sessionNumber">EXAMPLE OBSERVATION</Text><Title order={3}>Tradeoff explanation</Title><Text size="sm" c="dimmed">Qualitative · provisional · human review required</Text></div><div><blockquote>You named contention around a shared account row and proposed partitioning. The answer did not explain which consistency guarantee the alternative preserves.</blockquote><Text size="sm" c="dimmed">In the live report, this links to a corrected transcript span and exact rubric version.</Text><Divider my="lg" /><Text fw={700} c="assessment.7">Try next</Text><Text>State the invariant one option protects, its latency cost and a failure you would test.</Text></div></div>
          <Accordion variant="separated" className="plainAccordion"><Accordion.Item value="score"><Accordion.Control>Why no total score or percentile?</Accordion.Control><Accordion.Panel>One case per session has not been shown to support a stable rank or hiring decision. The pilot defaults to qualitative, evidence-linked feedback.</Accordion.Panel></Accordion.Item></Accordion>
        </section>}

        {step === 5 && <section aria-labelledby="rights-title" className="experience"><div className="sectionHeading"><Text className="eyebrow">06 / After the challenge</Text><Title order={2} id="rights-title">Your data controls.</Title><Text>The live product must show purpose, retention status and routes for withdrawal, access, correction and deletion with a receipt for each request.</Text></div>
          <div className="sessionList"><div className="sessionRow"><Text className="sessionNumber">01</Text><Title order={3}>Research choice</Title><Text>{research ? 'Research use selected in this preview.' : 'Research use not selected in this preview.'} No choice was saved.</Text></div><div className="sessionRow"><Text className="sessionNumber">02</Text><Title order={3}>Access and correction</Title><Text>Review the transcript and request correction or an export under the approved policy.</Text></div><div className="sessionRow"><Text className="sessionNumber">03</Text><Title order={3}>Deletion and withdrawal</Title><Text>See the request status and propagation receipt; a submitted request is not proof of completed deletion.</Text></div></div>
        </section>}

        <Group className="navigation" justify="space-between"><Button variant="subtle" disabled={step === 0} onClick={() => setStep(step - 1)}>Back</Button><Button onClick={step === 5 ? () => setStep(0) : advance}>{step === 5 ? 'Review again' : 'Next preview step'}</Button></Group>
      </Container>
    </main>
    <footer className="footer"><Container size="lg"><Stack gap={2}><Text size="sm">Mantine component-library prototype · candidate visual theme</Text><Text size="xs" c="dimmed">No recording, upload, analytics, storage or participant submission is implemented.</Text></Stack></Container></footer>
  </>;
}
