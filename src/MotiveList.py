import logging
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field

from GeneralInterval import IntervalList
from Motive import Motive
from MotivePosition import MotivePosition
from SequenceType import SequenceType


class IntervalClasses(BaseModel):
    interval_classes: Dict[SequenceType, IntervalList]

    @classmethod
    def from_intervals(cls, intervals: IntervalList) -> "IntervalClasses":
        inverted_intervals = intervals.inverted()
        mirrored_intervals = intervals.mirrored()
        mirrored_inverted_intervals = intervals.mirrored_inverted()
        return cls(
            interval_classes={
                SequenceType.ORIGINAL: intervals,
                SequenceType.INVERTED: inverted_intervals,
                SequenceType.MIRRORED: mirrored_intervals,
                SequenceType.MIRRORED_INVERTED: mirrored_inverted_intervals,
            }
        )

    def contains(self, intervals: IntervalList) -> bool:
        return any(
            intervals == interval_class
            for interval_class in self.interval_classes.values()
        )

    def get_sequence_type(self, intervals: IntervalList) -> Optional[SequenceType]:
        for sequence_type, interval_class in self.interval_classes.items():
            if interval_class == intervals:
                return sequence_type
        return None

    def name(self, sequence_type: SequenceType) -> str:
        return str(self.interval_classes[sequence_type])


def _default_positions() -> Dict[
    SequenceType, Dict[str, Dict[str, Dict[str, List[MotivePosition]]]]
]:
    return {
        SequenceType.ORIGINAL: {},
        SequenceType.INVERTED: {},
        SequenceType.MIRRORED: {},
        SequenceType.MIRRORED_INVERTED: {},
    }


class ResultMotive(BaseModel):
    intervals: IntervalClasses
    positions: Dict[
        SequenceType, Dict[str, Dict[str, Dict[str, List[MotivePosition]]]]
    ] = Field(default_factory=_default_positions)

    def get_sequence_type(self, motive: Motive) -> Optional[SequenceType]:
        interval_list = IntervalList(intervals=motive.sequence)
        return self.intervals.get_sequence_type(interval_list)

    def add(
        self,
        motive: Motive,
        sequence_type: SequenceType,
        piece_title: str,
        part_id: str,
        voice_id: str,
    ):
        self.positions[sequence_type].setdefault(piece_title, {}).setdefault(
            part_id, {}
        ).setdefault(voice_id, []).extend(motive.positions)

    def frequency(self, sequence_type: Optional[SequenceType] = None) -> int:
        if sequence_type is None:
            return count_elements_in_lists(self.positions)
        return count_elements_in_lists(self.positions[sequence_type])


def count_elements_in_lists(d: Any) -> int:
    if isinstance(d, list):
        return len(d)
    elif isinstance(d, dict):
        return sum(count_elements_in_lists(v) for v in d.values())
    return 0


class MotiveList(BaseModel):
    motives: List[ResultMotive]

    def add(
        self,
        candidate_motives: List[Motive],
        piece_title: str,
        part_id: str,
        voice_id: str,
    ):
        logging.info(f"Adding {len(candidate_motives)} candidate motives")
        for candidate_motive in candidate_motives:
            if len(self.motives) == 0:
                result_motive = ResultMotive(
                    intervals=IntervalClasses.from_intervals(
                        IntervalList(intervals=candidate_motive.sequence)
                    )
                )
                result_motive.add(
                    candidate_motive,
                    SequenceType.ORIGINAL,
                    piece_title,
                    part_id,
                    voice_id,
                )

                self.motives.append(result_motive)
                continue

            found_existing_motive = False
            for existing_motive in self.motives:
                sequence_type = existing_motive.get_sequence_type(candidate_motive)

                if sequence_type is not None:
                    existing_motive.add(
                        candidate_motive,
                        sequence_type,
                        piece_title,
                        part_id,
                        voice_id,
                    )
                    found_existing_motive = True
                    break

            if not found_existing_motive:
                result_motive = ResultMotive(
                    intervals=IntervalClasses.from_intervals(
                        IntervalList(intervals=candidate_motive.sequence)
                    )
                )
                result_motive.add(
                    candidate_motive,
                    SequenceType.ORIGINAL,
                    piece_title,
                    part_id,
                    voice_id,
                )

                self.motives.append(result_motive)

    def __len__(self):
        return len(self.motives)

    def __iter__(self):
        return iter(self.motives)

    def __getitem__(self, index):
        return self.motives[index]
