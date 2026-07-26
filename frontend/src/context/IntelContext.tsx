import { createContext, useContext, useState, ReactNode } from 'react';

interface IntelContextType {
  selectedDistrictId: string | null;
  selectedCaseId: string | null;
  selectedSuspectId: string | null;
  selectedPatternId: string | null;
  timeOfDayFilter: number;
  setSelectedDistrictId: (id: string | null) => void;
  setSelectedCaseId: (id: string | null) => void;
  setSelectedSuspectId: (id: string | null) => void;
  setSelectedPatternId: (id: string | null) => void;
  setTimeOfDayFilter: (time: number) => void;
  highlightTrigger: number;
  triggerHighlight: () => void;
}

const IntelContext = createContext<IntelContextType | undefined>(undefined);

export function IntelProvider({ children }: { children: ReactNode }) {
  const [selectedDistrictId, setSelectedDistrictIdState] = useState<string | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [selectedSuspectId, setSelectedSuspectId] = useState<string | null>(null);
  const [selectedPatternId, setSelectedPatternIdState] = useState<string | null>(null);
  const [timeOfDayFilter, setTimeOfDayFilter] = useState<number>(-1);
  const [highlightTrigger, setHighlightTrigger] = useState(0);

  const triggerHighlight = () => setHighlightTrigger((prev) => prev + 1);

  const setSelectedDistrictId = (id: string | null) => {
    setSelectedDistrictIdState(id);
    triggerHighlight();
  };

  const setSelectedPatternId = (id: string | null) => {
    setSelectedPatternIdState(id);
    triggerHighlight();
  };

  return (
    <IntelContext.Provider
      value={{
        selectedDistrictId,
        selectedCaseId,
        selectedSuspectId,
        selectedPatternId,
        timeOfDayFilter,
        setSelectedDistrictId,
        setSelectedCaseId,
        setSelectedSuspectId,
        setSelectedPatternId,
        setTimeOfDayFilter,
        highlightTrigger,
        triggerHighlight
      }}
    >
      {children}
    </IntelContext.Provider>
  );
}

export function useIntel() {
  const context = useContext(IntelContext);
  if (context === undefined) {
    throw new Error('useIntel must be used within an IntelProvider');
  }
  return context;
}
