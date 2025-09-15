import {expect, test, beforeEach, afterEach} from 'vitest'
import { render, screen, cleanup } from '@testing-library/svelte'
import userEvent from '@testing-library/user-event'
import Main from '../../src/lib/Main.svelte'

/** @type {ReturnType<typeof userEvent.setup>} */
let user

beforeEach(() => {
  user = userEvent.setup({ document })
  render(Main)
})

afterEach(() => {
	cleanup()
  })

test('Modal limitações', async () => {
  expect(screen.queryByTestId("limitacoes-modal")).not.toBeInTheDocument()
  await user.click(screen.getByTestId("limitacoes-btn"))
  expect(screen.getByTestId("limitacoes-modal")).toBeInTheDocument()
})

test('Modal LGPD', async () => {
  expect(screen.queryByTestId("lgpd-modal")).not.toBeInTheDocument()
  await user.click(screen.getByTestId("lgpd-btn"))
  expect(screen.getByTestId("lgpd-modal")).toBeInTheDocument()
})
