package org.motivesearch.csma

import org.hamcrest.MatcherAssert.assertThat
import org.hamcrest.Matchers.equalTo
import kotlin.test.Test

private const val sequence = "A,B,A,B,C,D,C,A,B,D,C,E"

class MotiveGeneratorTest {
    val underTest = MotiveGenerator()

    @Test
    fun `can get motive units from comma separated string`() {
        val motiveUnits = underTest.getMotiveUnits(sequence)

        assertThat(motiveUnits.size, equalTo(12))
        assertThat(motiveUnits[0].name, equalTo("A"))
    }

    @Test
    fun `can get basic motives from sequence`() {
        val motiveUnits = underTest.getMotiveUnits(sequence)
        val basicMotives = underTest.getBasicMotives(motiveUnits, 2)

        assertThat(basicMotives.size, equalTo(4))

        val firstMotiv = basicMotives[0]

        assertThat(firstMotiv.frequency, equalTo(3))
        assertThat(firstMotiv.sequence, equalTo(listOf(MotiveUnit("A"))))
        assertThat(
            firstMotiv.positions, equalTo(
                listOf(MotivePosition(0, 1), MotivePosition(2, 1), MotivePosition(7, 1))
            )
        )
    }

    @Test
    fun `can get frequent position`() {
        val motive = Motive.fromPositions(
            listOf(MotivePosition(0, 1), MotivePosition(2, 1), MotivePosition(7, 1)),
            listOf(MotiveUnit("A"))
        )

        val frequentPosition = underTest.getFrequentPosition(motive, 2)
        assertThat(frequentPosition, equalTo(3))
    }

    @Test
    fun `can generate candidate extensions`() {
        val motiveUnits = underTest.getMotiveUnits(sequence)
        val basicMotives = underTest.getBasicMotives(motiveUnits, 2)
        val candidateExtensions = underTest.generateCandidateExtension(basicMotives, 11)

        assertThat(candidateExtensions.size, equalTo(1))
        assertThat(candidateExtensions[0].sequence, equalTo(listOf(MotiveUnit("C"))))
        assertThat(candidateExtensions[0].positions, equalTo(basicMotives[2].positions))
    }


    @Test
    fun `can merge motives`() {
        val motiveUnits = underTest.getMotiveUnits(sequence)
        val basicMotives = underTest.getBasicMotives(motiveUnits, 2)
        val candidateExtensions = underTest.generateCandidateExtension(basicMotives, 4)

        val mergedMotive = underTest.mergeMotives(basicMotives[0], candidateExtensions[1], 1, 4)

        assertThat(mergedMotive.sequence, equalTo(listOf(MotiveUnit("A"), MotiveUnit("B"))))
        assertThat(
            mergedMotive.positions,
            equalTo(listOf(MotivePosition(0, 2), MotivePosition(2, 2), MotivePosition(7, 2)))
        )
        assertThat(mergedMotive.frequency, equalTo(3))
    }

    @Test
    fun `can detect motives`() {
        val motiveUnits = underTest.getMotiveUnits("A,B,A,B,C,D,C,A,B,D,C,E")
        val finalMotives = underTest.generateMotives(motiveUnits, 2, 1, 1, 4)

        assertThat(
            finalMotives, equalTo(
                listOf(
                    Motive(
                        listOf(MotivePosition(0, 2), MotivePosition(2, 2), MotivePosition(7, 2)),
                        3,
                        listOf(MotiveUnit("A"), MotiveUnit("B"))
                    ),
                    Motive(
                        listOf(MotivePosition(3, 2), MotivePosition(8, 2)),
                        2,
                        listOf(MotiveUnit("B"), MotiveUnit("C"))
                    ),
                    Motive(
                        listOf(MotivePosition(3, 2), MotivePosition(8, 2)),
                        2,
                        listOf(MotiveUnit("B"), MotiveUnit("D"))
                    ),
                    Motive(
                        listOf(MotivePosition(5, 2), MotivePosition(9, 2)),
                        2,
                        listOf(MotiveUnit("D"), MotiveUnit("C"))
                    ),
                    Motive(
                        listOf(MotivePosition(2, 3), MotivePosition(7, 3)),
                        2,
                        listOf(MotiveUnit("A"), MotiveUnit("B"), MotiveUnit("C"))
                    ),
                    Motive(
                        listOf(MotivePosition(2, 3), MotivePosition(7, 3)),
                        2,
                        listOf(MotiveUnit("A"), MotiveUnit("B"), MotiveUnit("D"))
                    ),
                    Motive(
                        listOf(MotivePosition(3, 3), MotivePosition(8, 3)),
                        2,
                        listOf(MotiveUnit("B"), MotiveUnit("C"), MotiveUnit("C"))
                    ),
                    Motive(
                        listOf(MotivePosition(3, 3), MotivePosition(8, 3)),
                        2,
                        listOf(MotiveUnit("B"), MotiveUnit("D"), MotiveUnit("C"))
                    ),
                )
            )
        )
    }
}